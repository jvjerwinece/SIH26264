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

## 2. Runtime today (v8)

The submission prototype is deliberately infrastructure-free:

```
Ekasutra_v8.html
  ├── embedded seed arrays (institutions, cases, overlaps, rooms, audit)
  ├── render functions per screen (dashboard, intake, radar, rooms, …)
  ├── in-memory state  ──persist()──▶  localStorage
  ├── SHA-256 implementation (Web Crypto or embedded fallback)
  └── self-contained CSS, fonts fallback, SVG icons
```

- **Entry point:** [`submission/Ekasutra_v8.html`](../submission/Ekasutra_v8.html). One file, no build step.
- **State:** `cases`, `institutions`, `audit`, `rooms`, `overlaps` arrays. `persist()` serialises the subset needed to survive reload; `applyState()` restores it.
- **Navigation:** `go(screen)` re-renders `#content` from state. No router, no framework.
- **Tour:** five scripted stops driven by a timer and highlighted selectors.
- **Audit:** `chainHash(prev, entry)` at line 1570, `rehashAudit()` at 1402, verification UI at 1571–1578.
- **Why this shape:** a judge can open the file on any laptop, offline, with no credentials, and see the whole product in under a minute. That is worth more at this stage than a deployed stack.

**What it is not:** there is no server, no authentication, no database connection, no file upload, and no concurrency control. The in-memory arrays mirror the seed, not a live database.

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

Auto-link rule used in the demo: **score ≥ 92 and margin ≥ 8 over the runner-up**. The reference case, `S.V. College of Engineering Kanchipuram`, resolves at **92.7** with a **58.4** runner-up (34.3-point margin). Mid-band candidates are surfaced for confirmation; below the threshold the intake stays unmatched rather than guessing.

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

**PostgreSQL:** `audit_write(actor, action, object)` reads the previous hash, computes the next, inserts. `audit_verify()` walks the chain oldest-first and returns the first broken row or `ok = true`. Demo head: `748b44fc1aad8e9a1c05d0040b54e95f68d966ea5396dffc789139aab9fc6fe0`.

**Browser:** the same formula over the in-memory `audit` array, rendered newest-first. `Verify chain` recomputes and compares.

**Defect, currently open:** `renderAudit()` calls `rehashAudit()` before verification, and `applyState()` calls it after loading. Any edited row is re-sealed, so the browser check cannot detect tampering. It is an internal-consistency check, not a tamper check. Details and fix in [`QA_REPORT.md`](QA_REPORT.md) (P1-1).

**Concurrency defect, currently open:** `audit_write()` reads the head with `order by id desc limit 1` and no lock. Two concurrent transactions can read the same predecessor and fork the chain. Fix: serialise on a chain-head row (`select … for update`) or `pg_advisory_xact_lock`, plus a unique index on `prev_hash`.

## 8. API contract (proposed, not built)

The database README defines the intended surface. Each endpoint is one query or one transaction; field names already match the view.

| Method | Path | Backing object |
|---|---|---|
| GET | `/api/cases` | `v_case_register` |
| GET | `/api/cases/:caseNo` | case + events + documents |
| GET | `/api/institutions` | institutions + aliases |
| POST | `/api/intake` | insert case, event, document, `audit_write` |
| POST | `/api/overlaps/:ref/link` | `overlap_cases`, room, activity |
| POST | `/api/rooms/:ref/decision` | lead bureau + joint decision, one transaction |
| POST | `/api/rooms/:ref/escalate` | reason required; live cases → Escalated |
| POST | `/api/rooms/:ref/merge` | `duplicate_of`, overlap merged, activity |
| GET | `/api/rooms/:ref/brief` | one-page brief, print-ready |
| POST | `/api/audit/verify` | `audit_verify()` |

## 9. Production shape (proposed)

Deck slide 3 names **Next.js · FastAPI · PostgreSQL · Docker**. That is a target, not the current build.

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
2. Transactional custody and room decisions; no client-supplied actor.
3. Locked audit append and a unique `prev_hash`.
4. Server-side document hashing and malware scanning.
5. PII classification, retention policy and access logging.
6. Backup/restore drill and an audit-export format for RTI/oversight.

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
| Single-file HTML | Zero-friction demo, offline, no credentials | No real persistence, no auth, no concurrency |
| In-memory arrays mirror the seed | Deterministic demo; chain can be checked | UI and DB drift after actions (see Data Layer defect) |
| Human-in-the-loop linking | Avoids silent false merges | Throughput depends on officer review |
| Append-only audit | Tamper-evident by construction | Storage grows; corrections need new rows |
| `pg_trgm` only | Core Postgres, explainable, no external service | Weaker on transliteration and very short names |
| Real institution names + synthetic cases | Realistic screenshots | Reputational risk; must be labelled persistently |

## 12. Files that matter

- Prototype: [`submission/Ekasutra_v8.html`](../submission/Ekasutra_v8.html)
- Schema: [`database/schema.sql`](../database/schema.sql)
- Seed: [`database/seed_demo.sql`](../database/seed_demo.sql)
- Matcher reference: [`database/README.md`](../database/README.md)
- Findings: [`docs/QA_REPORT.md`](QA_REPORT.md)
- Claim register: [`docs/DATA_NOTICE.md`](DATA_NOTICE.md)
