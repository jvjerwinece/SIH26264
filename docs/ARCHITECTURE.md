# Architecture

**Scope:** the v8 prototype as shipped, the PostgreSQL layer that backs it, and the production shape the team should build next. Anything labelled **proposed** is not implemented.

---

## 1. The design position

Most complaint dashboards are built around a case. Ekasutra is built around an **institution**. A case is one window into an institution's history; the institution is the unit that RB and PGRC actually share. That choice drives everything else:

1. **The Permanent ID is the join key.** Not a name, not a pincode, not an email. Every case, alias, overlap and room hangs from `institutions.permanent_id`.
2. **No silent merge.** A machine may suggest a link; a human confirms it. `overlap_clusters` records confidence and reasons; `rooms` records who decided and why. An absorbed duplicate keeps `cases.duplicate_of` and is never deleted.
3. **Custody is explicit.** Every case names a bureau, an officer, a last action and a next action. “Who owns this?” is a column, not an inference.
4. **Proof is a chain, not a claim.** Every action appends a row whose hash commits to the previous row. The same formula runs in the browser and in PostgreSQL.
5. **Coordinate, do not centralise the work.** RB and PGRC keep their own case records; the room is the shared surface where the joint decision is made.

## 2. Runtime today (v9, 29 October 2026)

The same product runs in two modes.

**Offline artifact.** [`submission/Ekasutra_v8.html`](../submission/Ekasutra_v8.html) remains the frozen submission file:

```
Ekasutra_v8.html
  ├── embedded seed arrays (institutions, cases, overlaps, rooms, audit)
  ├── render functions per screen (dashboard, intake, radar, rooms, …)
  ├── in-memory state  ──persist()──▶  localStorage
  ├── SHA-256 implementation (Web Crypto or embedded fallback)
  └── self-contained CSS, fonts fallback, SVG icons
```

It opens from `file://` with no network. `persist()` serialises the subset needed to survive reload; `applyState()` restores it. Navigation is `go(screen)` re-rendering `#content`; there is no framework.

**Demo stack.** [`web/`](../web) + [`server/`](../server) + [`database/`](../database) run a real three-tier deployment:

```
Vercel (web/)                        Render (server/)              Supabase (database/)
static dashboard + /api proxy  ──▶   FastAPI + psycopg pool   ──▶  PostgreSQL 16, schema.sql + seed
```

- [`web/index.html`](../web/index.html) is derived from the submission file and adds a live layer. `connectLive()` fetches `GET /api/bootstrap` and replaces the seed arrays; every write calls the API first and re-hydrates from PostgreSQL. From `file://`, or if the API is unreachable, the screen keeps the offline seed and says so.
- [`web/api/[...path].js`](../web/api/[...path].js) is a same-origin Vercel proxy to the Render service, so the browser only talks to the domain it loaded and Render needs no CORS entry.
- [`server/app.py`](../server/app.py) resolves the actor server-side from `X-Demo-Role` against the seeded users. No actor is accepted from the request body.
- **What it is not:** a pilot. There is still no login, no RBAC, uploads are metadata only, and every complaint is synthetic. `/api/meta` reports those limits in the payload, and the UI prints them on the Data Layer screen.

Deployment steps, environment variables and custom-domain DNS are in [`DEPLOYMENT.md`](DEPLOYMENT.md).

## 3. Data model

PostgreSQL 14+, one extension (`pg_trgm`), eleven tables, one view, one matcher, two audit functions. Source: [`database/schema.sql`](../database/schema.sql).

| Table | Purpose | Key invariant |
|---|---|---|
| `institutions` | Canonical institution master | `permanent_id` unique, regex `^[0-9]-[0-9]{6,10}$` |
| `institution_aliases` | Every spelling seen in a complaint | unique `(institution_id, alias)` |
| `users` | Officers, leads, directors, admin | role and bureau constrained |
| `cases` | Case ledger | status, bureau, transfer target, `duplicate_of` |
| `case_events` | Append-only chronology | corrections are new rows, never updates |
| `documents` | Evidence metadata | `sha256 char(64)` |
| `overlap_clusters` | Candidate overlap with confidence and reasons | state `open/dismissed/merged` |
| `overlap_cases` | Cases in a cluster | composite primary key |
| `rooms` | One coordination room per overlap | `overlap_id` unique; escalation requires actor + reason |
| `room_activity` | Room timeline | append-only |
| `audit_entries` | Hash chain | `prev_hash` + `hash`, 64 hex chars |

Derived at query time:

- `v_case_register` joins cases to institutions and computes `age_days` and `beyond_sla`, so the register is never stale.
- `fn_match_institution(name, state)` returns candidate rows with `score` and a human-readable `why` (exact ID, alias, trigram).

Demo seed: 18 institutions, 27 aliases, 9 users, 32 cases, 129 case events, 3 overlap clusters, 7 linked cases, 3 rooms, 5 room activities, 109 documents, 18 audit rows. See [`database/README.md`](../database/README.md).

## 4. Identity resolution

The matcher runs in four stages, cheapest and most certain first:

| Stage | Rule | Outcome |
|---|---|---|
| 1. Permanent ID | Exact match on `permanent_id` | Auto-link, no review |
| 2. Alias | Exact match in `institution_aliases` | Auto-link, show alias source |
| 3. Trigram | `similarity(name, alias/name)`, state-scoped | Score and reasons returned |
| 4. Human | Mid-band score or ambiguous candidates | Officer picks or rejects |

Auto-link rule used in the demo: **score ≥ 92 and margin ≥ 8 over the runner-up**. With `state = 'Tamil Nadu'`, `S.V. College of Engineering Kanchipuram` resolves at **92.7** against a **67.2** runner-up (25.5-point margin). Mid-band candidates are surfaced for confirmation; below the threshold the intake stays unmatched rather than guessing.

Two properties matter for the pitch:

- **No external service.** `pg_trgm` is in core PostgreSQL; the demo works without a vector database or a model endpoint.
- **Explainable.** Every match carries a `why` string; a judge can see the alias or the score instead of trusting a black box.

**Known gap:** the national-scale benchmark is not in this repository. See `DATA_NOTICE.md`.

## 5. Case and custody lifecycle

```
Received ──▶ Under Process ──▶ Disposed
                 │  ▲
                 │  └──────── Transferred (to RB / PGRC / RO)
                 ▼
             Escalated
```

- `cases.status` is constrained to `Pending`, `Under Process`, `Disposed`, `Transferred`, `Escalated`.
- `cases.transfer_to` is mandatory when status is `Transferred` (check constraint).
- `cases.expected_disposal` cannot precede `received_on`.
- `duplicate_of` points an absorbed duplicate at the lead case; the row is retained.
- SLA is `received_on + sla_days`; `v_case_register` computes `beyond_sla` at read time so no nightly job can leave it stale.

**Proposed for the next build:** promote custody to an explicit state machine with transitions, actor and timestamp per state, instead of deriving it from status + bureau + last action. The current model is sufficient for the demo and weaker under audit.

## 6. Overlap and coordination

```
intake / nightly scan
        │
        ▼
overlap_clusters (confidence, reason JSON, state=open)
        │  human reviews
        ├── dismiss ──▶ state=dismissed
        ├── related / conflict / systemic ──▶ room opened
        └── duplicate ──▶ merge ──▶ duplicate_of + state=merged
                                   │
                                   ▼
                            rooms (lead_bureau, custody, state)
                                   │
                     ┌─────────────┼──────────────┐
                     ▼             ▼              ▼
                joint decision  escalate       merge target
                     │             │              │
                     └──── room_activity (append-only) ────┘
```

- A room has exactly one overlap and at most one lead bureau.
- Escalation is legal only with `escalated_by` and `escalation_reason` (check constraint).
- Merge records `merged_into_case` on both the room and the cluster; the absorbed case stays linked.
- The printable brief is generated from the room, its cases, the decision and the activity trail — the same data, one page.

## 7. Audit ledger

**Formula, identical on both sides:**

```
hash = sha256( prev_hash
             ‖ to_char(at AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS.US')
             ‖ actor ‖ action ‖ object )
```

Genesis is `repeat('0', 64)`. The newest row commits to every row before it.

**PostgreSQL:** `audit_write(actor, action, object)` takes `pg_advisory_xact_lock(hashtext('ekasutra.audit_chain'))`, reads the previous hash, computes the next and inserts. The lock is held until the transaction ends, so two writers cannot read the same head. A unique index on `audit_entries.prev_hash` makes a fork fail immediately instead of silently surviving. Demo head: `748b44fc1aad8e9a1c05d0040b54e95f68d966ea5396dffc789139aab9fc6fe0`.

**Browser:** the same formula over the in-memory `audit` array, rendered newest-first. `Verify chain` recomputes and compares stored hashes without rewriting them; in live mode it calls `GET /api/audit/verify`, so PostgreSQL is the verifier.

**Concurrency evidence (29 October 2026):** a 20-writer parallel test took the chain from 18 to 38 rows with 38 distinct `prev_hash` values, zero duplicates, and `audit_verify()` returned `ok = true`. Before the lock and index, the same test could fork the chain.

## 8. API contract (implemented)

[`server/app.py`](../server/app.py) serves these routes. The browser sends `X-Demo-Role`; the server maps it to a seeded user and writes that name as the actor. Every write is one transaction: ledger change + `case_events` row + `audit_write()`.

| Method | Path | What it does |
|---|---|---|
| GET | `/health` | Process + database liveness, audit row count and `audit_verify()` result |
| GET | `/api/bootstrap` | Institutions (with aliases), cases, overlaps, rooms, latest 60 audit rows, table counts, chain state |
| GET | `/api/meta` | Version, PostgreSQL version, counts, chain state, demo limits (`auth: false`, uploads metadata only, synthetic data) |
| GET | `/api/audit?limit=` | Audit rows, newest first |
| GET | `/api/audit/verify` | `audit_verify()` result |
| GET | `/api/match?text=&state=&limit=` | `fn_match_institution` — server-side advisory matcher |
| POST | `/api/cases` | Create a case from a resolved Permanent ID; assigns the next `C-YYYY-NNNN`, category SLA, `created` event, audit row |
| POST | `/api/cases/{case_no}/actions` | `assign`, `transfer`, `dispose`, `reopen`, `docs`, `note` — row-locked, event + audit |
| POST | `/api/overlaps/{ref}/dismiss` | Human rejection of an overlap; 409 if already reviewed |
| POST | `/api/rooms/{ref}/actions` | `lead`, `decision`, `docs`, `merge`, `escalate` (reason required) |

Notes on behaviour that the UI relies on:

- `POST /api/cases` resolves the institution by `permanent_id`; unknown IDs return 404 rather than creating an orphan case.
- Case actions lock the case row (`select … for update`) before mutating, so two officers cannot dispose and reopen the same case concurrently.
- Merge picks the earliest received case as the lead, marks the others `duplicate_of`, sets the cluster and room to `merged`, and writes both events.
- Errors are `{"detail": "..."}` with 4xx/5xx status; the client prints the detail in a warning toast and keeps the screen unchanged.

## 9. Deployment shape (built) and production target

**Built: free-tier demo stack.**

```
Browser
  │  HTTPS, same origin
  ▼
Vercel — static web/ + api/[...path].js proxy
  │  server-to-server
  ▼
Render — Docker image from server/, uvicorn on $PORT
  │  DATABASE_URL, sslmode=require
  ▼
Supabase — PostgreSQL 16, Supavisor session pooler
```

- Render runs [`render.yaml`](../render.yaml) with `rootDir: server`; `healthCheckPath: /health`. `DB_POOL_MAX=5`, `prepare_threshold=None` for pooler compatibility.
- The Vercel function reads `EKASUTRA_API_ORIGIN` and forwards method, body, query and `X-Demo-Role`. No Render URL or database credential reaches the browser.
- Supabase receives [`database/Ekasutra_Supabase.sql`](../database/Ekasutra_Supabase.sql) (schema + seed concatenated, psql meta-commands stripped) through the SQL editor. Chain head after a clean load is `748b44fc…fc6fe0`; `/api/meta` exposes it.
- Custom domain points at Vercel only; Render stays on its `onrender.com` hostname behind the proxy.
- Free-tier behaviour: the Render service sleeps after idle and the Supabase project pauses after a week of inactivity. Both wake on the next request; the dashboard shows an offline seed until `/api/bootstrap` answers.
- Step-by-step runbook: [`DEPLOYMENT.md`](DEPLOYMENT.md).

**Production target.** Deck slide 3 names **Next.js · FastAPI · PostgreSQL · Docker**. Only FastAPI + PostgreSQL + Docker exist today; the Next.js officer UI does not.

```
Next.js (RB / PGRC officer UI)
        │  HTTPS, session cookie
        ▼
FastAPI  ── RBAC: officer / lead / director / admin, scoped by bureau
        │
        ├── PostgreSQL 14  (schema.sql, v_case_register, fn_match_institution)
        ├── object storage (documents; SHA-256 computed server-side)
        └── scheduler      (SLA alerts, overlap scan)
```

Minimum production gates before any pilot:

1. Authentication and bureau-scoped authorisation on every route.
2. Replace the `X-Demo-Role` switch with a session; keep the server-side actor resolution.
3. Server-side document upload, hashing and malware scanning (today: metadata rows only).
4. PII classification, retention policy and access logging.
5. Backup/restore drill and an audit-export format for RTI/oversight.
6. Load test on the production Postgres plan; the free tier is a demo host, not a capacity claim.

## 10. Where the team can spin off

The architecture is intentionally thin so the next team can deepen one layer without rewriting the rest.

- **Custody state machine.** Replace derived custody with explicit transitions and an append-only custody table; expose “who had it, when, and why it moved”.
- **Outcome ledger.** Today a case closes with a status. Add `outcomes` (finding, penalty, corrective action, closure evidence) and measure whether disposal actually fixed the institution's problem.
- **SLA policy engine.** `sla_days` is per case; move to policy by category, bureau and institution risk, with pause/resume for time spent waiting on the institution.
- **Duplicate detection at scale.** Add blocking keys (state + trigram prefix), evaluate precision/recall on a labelled set, and publish the harness with the repo.
- **Institution timeline.** One chronological thread across RB, PGRC and RO, including documents and outcomes; this is the strongest differentiator against a case-list dashboard.
- **Brief generation.** Expand the one-page room brief into a decision pack with evidence and dissent.
- **Analytics.** Region/bureau/status reports exist as screens; add cohort views (repeat institutions, systemic categories, time-to-first-action).

## 11. Trade-offs and limits

| Decision | Benefit | Cost |
|---|---|---|
| Single-file HTML, still shipped | Zero-friction offline demo, no credentials | No auth; offline mode has no real persistence |
| Live mode re-hydrates after every write | Screen and database cannot drift | One extra round trip per action |
| Human-in-the-loop linking | Avoids silent false merges | Throughput depends on officer review |
| Append-only audit | Tamper-evident by construction | Storage grows; corrections need new rows |
| `pg_trgm` only | Core Postgres, explainable, no external service | Weaker on transliteration and very short names |
| Free-tier Render + Supabase | Real three-tier deployment at zero cost | Cold starts after idle; paused database after a week |
| Fictional institution names in the demo seed | No reputational pairing of real colleges with invented allegations | Less familiar than the AICTE master names |

## 12. Files that matter

- Prototype (frozen): [`submission/Ekasutra_v8.html`](../submission/Ekasutra_v8.html)
- Deployed frontend: [`web/index.html`](../web/index.html), [`web/api/[...path].js`](../web/api/[...path].js)
- API: [`server/app.py`](../server/app.py), [`server/db.py`](../server/db.py), [`server/Dockerfile`](../server/Dockerfile)
- Schema: [`database/schema.sql`](../database/schema.sql)
- Seed: [`database/seed_demo.sql`](../database/seed_demo.sql)
- Supabase bundle: [`database/Ekasutra_Supabase.sql`](../database/Ekasutra_Supabase.sql)
- Deployment: [`render.yaml`](../render.yaml), [`web/vercel.json`](../web/vercel.json), [`DEPLOYMENT.md`](DEPLOYMENT.md)
- Matcher reference: [`database/README.md`](../database/README.md)
- Findings: [`docs/QA_REPORT.md`](QA_REPORT.md)
- Claim register: [`docs/DATA_NOTICE.md`](DATA_NOTICE.md)
