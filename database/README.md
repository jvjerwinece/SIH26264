# Ekasutra · database pack

PostgreSQL 14+. One extension (`pg_trgm`), eleven tables, one register view, one
matcher, one hash chain. This is the layer behind the dashboard, not a sketch of one.

```
schema.sql                  tables, indexes, v_case_register, fn_match_institution,
                            audit_write(), audit_verify()
demo_seed.json              the seed in readable form (18 institutions, 32 cases, 18 audit rows)
seed_demo.sql               generated, ready to load; refuses a non-empty database
generate_demo_seed.py       regenerates seed_demo.sql from the JSON
seed_institutions.py        builds institutions.csv from the AICTE list (9,558 rows)
../submission/Ekasutra_Data_Appendix.pdf
                            the schema, resolver and audit chain, written up
README.md                   this file
```

## 1. Load the demo database

The demo always goes into its **own** database. The national institution master
lives in another one, so a demo load can never touch it.

```bash
createdb ekasutra_demo
psql -d ekasutra_demo -f schema.sql
psql -d ekasutra_demo -f seed_demo.sql
```

The seed sets `client_encoding = 'utf8'` before inserting. Keep it: audit hashes
are computed over UTF-8 bytes, and a Windows psql session that defaults to
`WIN1252` will transcode the one non-ASCII audit object into mojibake and break
`audit_verify()` at that row.

The last command prints a row count for all eleven tables, then:

```
 entries | ok | broken_at
---------+----+-----------
      18 | t  |
```

and the chain head:

```
748b44fc1aad8e9a1c05d0040b54e95f68d966ea5396dffc789139aab9fc6fe0
```

That is the same value shown on the **Data Layer** screen of the dashboard, and
the same value the browser computes after you press **Verify chain** on the Audit
Log. Both sides hash the same bytes:

```
sha256( prev_hash || to_char(at at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.US')
        || actor || action || object )
```

Genesis is `repeat('0', 64)`. The newest row commits to all rows before it.

### The guard

`seed_demo.sql` starts with:

```sql
do $$ begin
  if (select count(*) from institutions) <> 0
     or (select count(*) from users) <> 0
     or (select count(*) from cases) <> 0
     or (select count(*) from audit_entries) <> 0 then
    raise exception 'seed_demo.sql: target database is not empty. ...';
  end if;
end $$;
```

Running it twice fails loudly and changes nothing. It cannot wipe the master.

## 2. Load the national master (separate database)

```bash
python3 seed_institutions.py institutions.json institutions.csv
createdb ekasutra
psql -d ekasutra -f schema.sql
psql -d ekasutra -c "\copy institutions(permanent_id, name, city, state) from 'institutions.csv' csv"
```

9,558 rows. The demo seed never writes here.

## 3. What each table holds

| table | demo rows | purpose |
|---|---:|---|
| `institutions` | 18 | AICTE Permanent ID is the join key (9,558 nationally) |
| `institution_aliases` | 27 | spellings seen in complaints, one row each |
| `users` | 9 | officers, one lead, director, admin |
| `cases` | 32 | the ledger: bureau, status, SLA, officer, next action |
| `case_events` | 129 | append-only chronology, four events per case plus one escalation |
| `documents` | 109 | filename, MIME, size, SHA-256, storage key, uploader |
| `overlap_clusters` | 3 | duplicate detections with confidence and JSON reasons |
| `overlap_cases` | 7 | which cases belong to which cluster |
| `rooms` | 3 | one coordination room per open cluster |
| `room_activity` | 5 | room timeline |
| `audit_entries` | 18 | SHA-256 hash chain |

`v_case_register` joins cases to institutions and computes `age_days` and
`beyond_sla` at query time, so the register is never stale.

## 4. Five queries worth showing

```sql
-- the filtered register
select case_no, institution, bureau, status, age_days, beyond_sla
from v_case_register order by received_on desc limit 10;

-- the duplicate that matters
select o.ref, o.confidence, count(oc.case_id) as linked, r.ref as room
from overlap_clusters o
join overlap_cases oc on oc.overlap_id = o.id
left join rooms r on r.overlap_id = o.id
group by o.ref, o.confidence, r.ref;

-- entity resolution: alias graph + trigram, no external service
select name, permanent_id, score, why
from fn_match_institution('S.V. College of Engineering Kanchipuram', 'Tamil Nadu');

-- the chain, recomputed in SQL
select * from audit_verify();

-- the head to compare with the dashboard
select hash from audit_entries order by id desc limit 1;
```

`fn_match_institution('S.V. College of Engineering Kanchipuram', 'Tamil Nadu')` returns
`92.7` for the SVCE alias with a `67.2` runner-up — a 25.5-point margin, past the
auto-link rule (>= 92 with >= 8 points of margin). Without the state hint the same
name scores `87.7`, which correctly falls to human confirmation.

## 5. Hashing a document at insert time

The browser uploads, the API hashes, Postgres stores the digest:

```sql
insert into documents (case_id, filename, mime, bytes, sha256, storage_key, uploaded_by)
values ((select id from cases where case_no = 'C-2026-0142'),
        'fee-receipt.pdf', 'application/pdf', 184320,
        encode(sha256(convert_to('…file bytes…', 'UTF8')), 'hex'),
        'demo/C-2026-0142/fee-receipt.pdf',
        (select id from users where email = 'p.rao@aicte.gov.in'));
```

For real files, hash the byte stream before upload and store the digest with the
object key. `documents.sha256` is `char(64)` for a reason.

## 6. Connecting the dashboard

The HTML file is deliberately credential-free: it runs from `file://`, holds the
same 32 cases in memory, and works with no network. To go live, put a thin API in
front of this database:

```
GET  /api/cases            -> select * from v_case_register
GET  /api/cases/:caseNo    -> case + case_events + documents
GET  /api/institutions     -> institutions + aliases
POST /api/intake           -> insert case, event, document, audit_write(...)
POST /api/overlaps/:ref/link -> insert overlap_cases, room, room_activity
POST /api/rooms/:ref/decision -> lead bureau + joint decision, one transaction
POST /api/rooms/:ref/escalate -> reason required; live cases -> Escalated
POST /api/rooms/:ref/merge    -> duplicate_of + overlap state 'merged' + room activity
GET  /api/rooms/:ref/brief    -> one-page coordination brief (print-ready)
POST /api/audit/verify     -> select * from audit_verify()
```

Rooms carry their own escalation reason and merge target. Absorbed duplicates
stay linked through `cases.duplicate_of`; nothing is deleted. The field names in
the API are already the column names in the view, so each screen needs one fetch
function, not a rewrite. Keep the DSN in the server
environment (`DATABASE_URL`), never in the browser.

## 7. Regenerating the seed

```bash
python3 generate_demo_seed.py
```

Same JSON in, byte-identical SQL out. It also prints the chain head, which must
stay `748b44fc…fc6fe0` unless `demo_seed.json` changes. If it does change, the
dashboard stores the same audit rows, so update both together and re-run
`audit_verify()`.
