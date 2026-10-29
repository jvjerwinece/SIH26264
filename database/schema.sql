-- ============================================================================
-- Ekasutra · SIH26264
-- PostgreSQL 14+ schema for the AICTE institution case coordination layer.
--
-- Design notes
--   * institutions.permanent_id is the join key everything else hangs from.
--   * cases is the ledger; case_events is append-only human history.
--   * overlap_clusters/overlap_cases detect the duplicate; rooms/room_activity resolve it.
--   * audit_entries is a hash chain: every row commits to the previous row.
--   * Matching uses pg_trgm only. No vector database, no external service.
-- ============================================================================

-- Supabase installs extensions into an `extensions` schema. Keep both schemas
-- resolvable so the trigram operator class and functions work on either layout.
set search_path = public, extensions;

create extension if not exists pg_trgm;

-- ---------------------------------------------------------------- institutions
create table institutions (
  id            bigint generated always as identity primary key,
  permanent_id  text not null unique check (permanent_id ~ '^[0-9]-[0-9]{6,10}$'),
  name          text not null,
  address       text,
  city          text,
  state         text,
  region        text check (region in ('South','West','North','East','Central')),
  trust_name    text,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

create index institutions_name_trgm on institutions using gin (name gin_trgm_ops);
create index institutions_region     on institutions (region);

-- Alias graph: one row per spelling variant seen in a complaint.
create table institution_aliases (
  id             bigint generated always as identity primary key,
  institution_id bigint not null references institutions(id) on delete cascade,
  alias          text not null,
  source         text not null default 'manual'
                 check (source in ('master','complaint','manual')),
  created_at     timestamptz not null default now(),
  unique (institution_id, alias)
);

create index institution_aliases_trgm on institution_aliases using gin (alias gin_trgm_ops);

-- ----------------------------------------------------------------------- users
create table users (
  id        bigint generated always as identity primary key,
  email     text not null unique,
  full_name text not null,
  role      text not null check (role in ('officer','lead','director','admin')),
  bureau    text check (bureau in ('RB','PGRC','RO')),
  active    boolean not null default true
);

-- ----------------------------------------------------------------------- cases
create table cases (
  id                bigint generated always as identity primary key,
  case_no           text not null unique,
  institution_id    bigint not null references institutions(id),
  bureau            text not null check (bureau in ('RB','PGRC','RO')),
  category          text not null,
  status            text not null default 'Pending'
                    check (status in ('Pending','Under Process','Disposed','Transferred','Escalated')),
  transfer_to       text check (transfer_to in ('RB','PGRC','RO')),
  duplicate_of      bigint references cases(id),  -- absorbed duplicate keeps a link to the lead case
  received_on       date not null,
  sla_days          int  not null default 60 check (sla_days between 1 and 365),
  officer_id        bigint references users(id),
  last_action       text,
  last_action_on    date,
  next_action       text,
  expected_disposal date,
  summary           text,
  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now(),
  check (expected_disposal is null or expected_disposal >= received_on),
  check (status <> 'Transferred' or transfer_to is not null),
  check (duplicate_of is null or duplicate_of <> id)
);

create index cases_institution on cases (institution_id, received_on desc);
create index cases_bureau      on cases (bureau);
create index cases_open        on cases (received_on) where status <> 'Disposed';

-- Append-only chronology. Rows are never updated; corrections are new rows.
create table case_events (
  id      bigint generated always as identity primary key,
  case_id bigint not null references cases(id) on delete cascade,
  at      timestamptz not null default now(),
  actor   text not null,
  kind    text not null check (kind in
          ('created','assigned','note','document','transfer','escalation','disposal','linked','merged','reopen')),
  detail  text not null
);

create index case_events_case on case_events (case_id, at);

-- -------------------------------------------------------------------- overlaps
create table overlap_clusters (
  id             bigint generated always as identity primary key,
  ref            text not null unique,
  institution_id bigint not null references institutions(id),
  confidence     numeric(5,2) not null check (confidence between 0 and 100),
  state          text not null default 'open'
                 check (state in ('open','dismissed','merged')),
  reason         jsonb not null default '[]'::jsonb,
  detected_at    timestamptz not null default now(),
  reviewed_by    bigint references users(id),
  reviewed_at    timestamptz,
  review_note    text,
  merged_into_case bigint references cases(id),
  merged_at        timestamptz
);

create index overlap_clusters_open on overlap_clusters (institution_id) where state = 'open';

create table overlap_cases (
  overlap_id bigint not null references overlap_clusters(id) on delete cascade,
  case_id    bigint not null references cases(id)    on delete cascade,
  primary key (overlap_id, case_id)
);

-- ------------------------------------------------------------- coordination
create table rooms (
  id          bigint generated always as identity primary key,
  ref         text not null unique,
  overlap_id  bigint not null unique references overlap_clusters(id) on delete cascade,
  lead_bureau text check (lead_bureau in ('RB','PGRC','RO')),  -- null = unassigned
  custody     text,
  state       text not null default 'open' check (state in ('open','closed')),
  escalated_at       timestamptz,
  escalated_by       bigint references users(id),
  escalation_reason  text,
  merged_into_case   bigint references cases(id),
  opened_at   timestamptz not null default now(),
  closed_at   timestamptz,
  check (escalated_at is null or (escalated_by is not null and escalation_reason is not null))
);

create table room_activity (
  id      bigint generated always as identity primary key,
  room_id bigint not null references rooms(id) on delete cascade,
  at      timestamptz not null default now(),
  actor   text not null,
  action  text not null
);

create index room_activity_room on room_activity (room_id, at);

-- ------------------------------------------------------------------- documents
create table documents (
  id          bigint generated always as identity primary key,
  case_id     bigint not null references cases(id) on delete cascade,
  filename    text not null,
  mime        text not null,
  bytes       bigint not null check (bytes > 0),
  sha256      char(64) not null,
  storage_key text not null,
  uploaded_by bigint references users(id),
  uploaded_at timestamptz not null default now()
);

create index documents_case on documents (case_id);

-- --------------------------------------------------------------- audit chain
create table audit_entries (
  id        bigint generated always as identity primary key,
  at        timestamptz not null default now(),
  actor     text not null,
  action    text not null,
  object    text not null,
  prev_hash char(64) not null,
  hash      char(64) not null
);

-- One successor per link. A forked chain breaks this index immediately.
create unique index audit_entries_prev on audit_entries (prev_hash);

-- Write one link. Every row commits to the previous row's hash.
create or replace function audit_write(p_actor text, p_action text, p_object text)
returns char(64)
language plpgsql as $$
declare
  v_prev char(64);
  v_at   timestamptz := clock_timestamp();
  v_hash char(64);
begin
  -- Serialise the append. Without this, two concurrent writers can read the
  -- same head and fork the chain; the lock is held until the transaction ends.
  perform pg_advisory_xact_lock(hashtext('ekasutra.audit_chain'));

  select hash into v_prev from audit_entries order by id desc limit 1;
  v_prev := coalesce(v_prev, repeat('0', 64));

  v_hash := encode(sha256(convert_to(
              v_prev
              || to_char(v_at at time zone 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS.US')
              || p_actor || p_action || p_object, 'UTF8')), 'hex');

  insert into audit_entries (at, actor, action, object, prev_hash, hash)
  values (v_at, p_actor, p_action, p_object, v_prev, v_hash);

  return v_hash;
end $$;

-- Recompute the chain. Returns the first broken row, or ok = true.
create or replace function audit_verify()
returns table (entries bigint, ok boolean, broken_at bigint)
language plpgsql as $$
declare
  r record;
  v_prev char(64) := repeat('0', 64);
  v_hash char(64);
  n bigint := 0;
  bad bigint := null;
begin
  for r in select * from audit_entries order by id loop
    v_hash := encode(sha256(convert_to(
                v_prev
                || to_char(r.at at time zone 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS.US')
                || r.actor || r.action || r.object, 'UTF8')), 'hex');
    n := n + 1;

    if v_hash <> r.hash or r.prev_hash <> v_prev then
      bad := r.id;
      exit;
    end if;

    v_prev := r.hash;
  end loop;

  return query select n, bad is null, bad;
end $$;

-- --------------------------------------------------------------- read models
create or replace view v_case_register as
select c.case_no,
       i.name           as institution,
       i.permanent_id,
       i.region,
       c.bureau,
       c.status,
       c.category,
       c.received_on,
       case when c.status = 'Disposed'
            then coalesce(c.last_action_on, c.received_on) - c.received_on
            else current_date - c.received_on end as age_days,
       c.sla_days,
       (c.status <> 'Disposed' and current_date - c.received_on > c.sla_days) as beyond_sla,
       c.next_action
from cases c
join institutions i on i.id = c.institution_id;

-- Entity resolution: official name + alias graph + optional state, trigram only.
--   select * from fn_match_institution('S.V. College of Engineering Kanchipuram', 'Tamil Nadu');
--
-- How to read the score: 0.7 x best(name, alias) + 0.3 x word similarity, plus a
-- 5 point bonus when the state on the complaint matches the master. The caller
-- decides whether to auto-link: in Ekasutra, only >= 92 with a >= 8 point margin
-- over the runner-up is auto-linked, and everything else is human-confirmed.
create or replace function fn_match_institution(
  p_text  text,
  p_state text default null,
  p_limit int  default 3
)
returns table (
  institution_id bigint,
  name           text,
  permanent_id   text,
  state          text,
  score          numeric,
  why            text
)
language sql stable
set search_path = public, extensions
as $$
  with cand as (
    select i.id,
           i.name,
           i.permanent_id,
           i.state,
           similarity(i.name, p_text)            as s_name,
           word_similarity(p_text, i.name)       as ws_name,
           coalesce((select max(greatest(similarity(a.alias, p_text),
                                          word_similarity(a.alias, p_text)))
                     from institution_aliases a
                     where a.institution_id = i.id), 0) as s_alias
    from institutions i
    where similarity(i.name, p_text) >= 0.20
       or word_similarity(p_text, i.name) >= 0.45
       or exists (select 1 from institution_aliases a
                  where a.institution_id = i.id
                    and greatest(similarity(a.alias, p_text), word_similarity(a.alias, p_text)) >= 0.20)
  )
  select c.id,
         c.name,
         c.permanent_id,
         c.state,
         round((100 * (0.7 * greatest(c.s_name, c.s_alias) + 0.3 * c.ws_name)
               + case when p_state is not null and lower(c.state) = lower(p_state) then 5 else 0 end)::numeric, 1) as score,
         concat_ws(' · ',
           'name ' || round(100 * c.s_name)::int,
           'word ' || round(100 * c.ws_name)::int,
           case when c.s_alias > 0 then 'alias ' || round(100 * c.s_alias)::int end,
           case when p_state is not null and lower(c.state) = lower(p_state) then 'same state' end
         ) as why
  from cand c
  order by score desc, c.name
  limit p_limit;
$$;
