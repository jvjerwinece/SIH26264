# Ekasutra

**SIH 2026 · Problem Statement 26264** — an integrated institution complaint and coordination dashboard for AICTE.

> One institution. One thread. One owner. One proof.

Ekasutra joins every complaint about an institution — across the **Regulation Bureau (RB)** and the **Public Grievance Redressal Cell (PGRC)** — onto that institution's **AICTE Permanent ID**. Duplicate complaints become one owned case with a joint decision, a named lead bureau, and an append-only audit trail. Nothing is merged silently: every link is confirmed by a human.

**Build:** v9.4, cut 29 October 2026 · **Upload deadline:** 28 October 2026
**State:** prototype, submission documents and a deployable three-tier demo stack complete · demo video **not recorded** · hosted URLs not yet provisioned · known evidence defects documented below.

---

## The problem

AICTE receives the same institution's problem through more than one window. RB sees approvals, inspections and compliance; PGRC sees student and staff grievances. The same college arrives with a different spelling, a different case number and a different clock. The institution is asked for the same documents twice, one bureau closes its file while the other is still open, and no single screen answers “who owns this institution right now?”

The problem statement asks for a single-window dashboard with eight capabilities: one view, current bureau, full movement, overlap detection, de-duplication, status monitoring, reports, and timeline alerts. Ekasutra implements all eight in the prototype.

## What the product does

- **Identity resolution.** Permanent ID first, alias graph second, trigram similarity third. Exact Permanent ID wins; alias match is shown with evidence; fuzzy matches above the auto-link rule (score ≥ 92 and margin ≥ 8) link automatically, mid-band matches go to a human, everything else stays unmatched.
- **Collision check at intake.** Before a new case is created, the intake screen shows open cases at the same institution and forces a choice: link, joint case, or proceed with a written reason.
- **Overlap classes that mean something.** Duplicate, related, conflict and systemic are different states with different actions. A duplicate merges; a conflict escalates; a systemic pattern opens a room.
- **Coordination rooms.** One room per open overlap, with a lead bureau, named owners, activity timeline, joint decision, escalation reason, merge target and a printable one-page brief.
- **Custody and SLA.** Every case names its current bureau and officer, its next action, its age and whether it is beyond SLA. Custody is explicit, not inferred.
- **Append-only ledger.** Every action is written as `sha256(prev_hash ‖ UTC time ‖ actor ‖ action ‖ object)`. The browser and PostgreSQL can compute the same chain. A tamper-evident history is the accountability layer, not a log file.
- **Advisory text similarity.** A TF-IDF cosine layer over complaint narratives flags differently-worded complaints — including cases at different institutions that identifier rules cannot link — and drafts a two-line brief of the incoming complaint. Both run in the browser, offline, and never link anything without an officer.
- **Works offline.** The submission prototype is one HTML file, no server, no credentials, and opens from `file://` on a laptop or phone.
- **Runs live too.** [`web/`](web) is the same dashboard wired to a FastAPI service ([`server/`](server)) over the PostgreSQL pack ([`database/`](database)). Writes commit inside one transaction with an audit row, and the screen re-hydrates from the database after each write. Deploy with [`render.yaml`](render.yaml) + [`web/vercel.json`](web/vercel.json) following [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md). It is a demo, not a pilot: no login, uploads are metadata only.

## Quick start

1. Open [`submission/Ekasutra_v8.html`](submission/Ekasutra_v8.html) in Chrome or Edge.
2. Click **90-sec tour** on the dashboard, or drive it manually:
   **Case Intake → Load sample → Resolve & check → Create joint case → Coordination Rooms → CR-01 → set lead bureau → joint decision → Escalate / Merge duplicate case / Export coordination brief → Audit Log → Verify chain.**
3. Reset from the profile menu (top-right avatar) → **Reset demo data**.

No install, no network, no API keys. State is stored in `localStorage` and survives reload until reset.

To run the live stack instead — FastAPI on Render, PostgreSQL on Supabase, the dashboard on Vercel and your own domain — follow [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md). Locally, `cd server && uvicorn app:app --port 8000` serves both the API and `web/`.

## Repository map

```
ekasutra/
├── submission/            the upload artifacts, byte-for-byte
│   ├── Ekasutra_v8.html
│   ├── Ekasutra_SIH2026_SIH26264_Official.pptx   ← portal upload (official SIH 2026 template)
│   ├── Ekasutra_SIH2026_SIH26264_Official.pdf    ← the PDF the portal asks for
│   ├── Ekasutra_SIH2026_SIH26264.pptx            long-form deck
│   ├── Ekasutra_SIH2026_SIH26264_preview.pdf
│   ├── Ekasutra_Data_Appendix.pdf
│   ├── Ekasutra_Submission_Kit.pdf
│   ├── Ekasutra_Database_Pack.zip
│   └── SHA256SUMS.txt
├── database/              the database pack, unpacked for review
│   ├── schema.sql         11 tables, register view, matcher, audit functions
│   ├── seed_demo.sql      deterministic demo seed (18 institutions, 32 cases)
│   ├── Ekasutra_Supabase.sql        fresh-project bundle (schema + seed)
│   ├── Ekasutra_Supabase_Reset.sql  truncate + reseed an existing demo project
│   ├── demo_seed.json     readable seed source
│   ├── generate_demo_seed.py
│   ├── seed_institutions.py
│   └── README.md          load, verify and API notes
├── server/                FastAPI demo API and Docker image for Render
│   ├── app.py             endpoints, transactional writes, server-side actor
│   ├── db.py              psycopg pool with a checkout probe
│   ├── requirements.txt
│   └── Dockerfile
├── web/                   deployable dashboard (derived from submission/Ekasutra_v8.html)
│   ├── index.html         offline seed + live mode on /api/bootstrap
│   ├── config.js          optional direct API base; empty when proxied
│   ├── vercel.json
│   └── api/[...path].js   same-origin proxy to Render
├── docs/
│   ├── ARCHITECTURE.md    domain model, matching, ledger, deployment, production gates
│   ├── DEPLOYMENT.md      Vercel + Render + Supabase + custom-domain runbook
│   ├── QA_REPORT.md       what passed, what is broken, evidence and grade
│   ├── DATA_NOTICE.md     what is real, what is synthetic, claim register
│   ├── SUBMISSION_CHECKLIST.md
│   ├── PS26264_MAPPING.md objective-by-objective mapping
│   ├── screenshots/       v8 QA captures (desktop, mobile, flows)
│   └── deck-preview/      one PNG per slide
├── qa/                    Playwright reproduction harness
├── tools/                 deck build scripts and the Supabase bundle builder
│   ├── SIH2026-IDEA-Presentation-Format.pptx   unmodified official template
│   ├── build_official_deck.py  rebuilds the portal deck from that template
│   └── pptx2pdf.ps1            exports PPTX → PDF through PowerPoint
├── render.yaml            Render Blueprint for the API
├── .env.example           required variables for Render and Vercel
├── CONTRIBUTING.md
├── CHANGELOG.md
└── README.md
```

## What is actually verified

Verified on 27 October 2026 against the files in this repository; deployment rows added 29 October 2026.

| Check | Result |
|---|---|
| Prototype opens offline from `file://`; nine screens navigate; console clean | Pass, no console or page errors at 1366×900 |
| Responsive layout | Pass at 320, 360, 390, 768, 1024, 1366, 1920 px; 0 px horizontal overflow at every width |
| Intake → resolve → joint case → room decision → audit verify | Pass; chain reports 18 events after reset |
| Demo seed chain | Head `748b44fc1aad…fc6fe0`; independently recomputed, 0 broken links |
| Database model | 11 tables, constraints, `v_case_register`, `fn_match_institution`, seed guard |
| Deck — official template | `Ekasutra_SIH2026_SIH26264_Official.pptx`: 6 slides built inside the downloaded SIH 2026 Idea format, instructions slide deleted; page 3 system flow and page 5 overlap chart drawn with native shapes from the seeded counts; page 5 also carries an 8-row status-quo vs Ekasutra table; one bureau colour system across pages 2/3/5; PDF exported from PowerPoint, 6 pages at 960×540 pt |
| Deck — long-form | 6 slides, 16:9; preview PDF matches; embedded screenshots are v8 cream UI |
| Kit and appendix | 2 pages each, render checked |
| PS 26264 objectives | 8 of 8 mapped in the prototype (see `docs/PS26264_MAPPING.md`) |
| Demo video | **Not recorded** — blocking submission item |
| Audit append under concurrency | Pass on 29 October: 20 parallel writers took the chain from 18 to 38 rows, 38 distinct `prev_hash` values, 0 duplicates, `audit_verify()` ok |
| Live stack, local end to end | Pass on PostgreSQL 16.15 + FastAPI + Chromium: intake create, dispose, role-switched reopen all committed; UI counts equalled SQL counts; chain verified in PostgreSQL from the Data Layer screen |
| Vercel proxy handler | Pass against the local API: bootstrap 200, verify 200, matcher 200, invalid POST 422, `..` path blocked 400 |
| Hosted deployment | **Not yet provisioned** — needs the Supabase, Render and Vercel accounts and DNS access; runbook in `docs/DEPLOYMENT.md` |

**Not verified, and must not be claimed as built:** a hosted instance on Supabase/Render/Vercel (the configs are ready, the URLs are not), authentication/RBAC, real file upload, Supavisor and cold-start behaviour on the real free tiers, national-scale matcher benchmark, and any evaluation over the full 9,558-name master. The shipped evaluation is 367 labelled name variants. See `docs/QA_REPORT.md`.

## Read before presenting

The five P1 defects from the 26 October audit were fixed on 27 October and re-tested. Details and evidence are in [`docs/QA_REPORT.md`](docs/QA_REPORT.md).

1. **Browser audit verification now detects tampering.** The stored chain is verified without re-hashing; editing a row and pressing **Verify chain** reports “Chain broken”.
2. **Data Layer reads the live newest entry** and explains that the psql comparison is against the seeded 18-row snapshot.
3. **Institution documents carry unique digests** derived per institution and filename.
4. **The team slide shows six people** (lead 1, frontend + design 2, backend 2, data 1) and the notes match.
5. **Every artifact uses one set of numbers:** 9,558-ID master, 367 labelled variants, 94.6% top-1, 99.7% top-3, zero silent merges. The old 2,726 / 95.0 / 98.2 / 100% / 70.3% / 322 claims are gone from the prototype, deck, preview, kit and appendix.

Still open: the video is not recorded; the three-tier stack is built and verified locally but not yet deployed to Supabase/Render/Vercel (runbook ready); there is no authentication, RBAC or real upload; and the national-scale matcher benchmark is not shipped. The audit append is now concurrency-locked and the demo API is real, so neither should be listed as missing.

## Data

Complaints, people, documents and audit rows are **synthetic**. Institution names are drawn from the public AICTE list, which creates a reputational risk when paired with fabricated allegations. Do not present the demo as real case data. Read [`docs/DATA_NOTICE.md`](docs/DATA_NOTICE.md) before publishing screenshots or recording the video.

## Checksums

`submission/SHA256SUMS.txt` covers the six upload files. Verify before uploading:

```bash
cd submission
sha256sum -c SHA256SUMS.txt
```

On Windows PowerShell:

```powershell
Get-FileHash .\Ekasutra_v8.html -Algorithm SHA256
```

The checksum file uses LF line endings and is pinned by `.gitattributes` so the bytes do not change on checkout.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Short version: branch from `main`, do not edit files under `submission/` in place without regenerating checksums, keep synthetic data labelled, and never add real complaint data or personal information to this repository.

## Ownership

Internal team repository for SIH 2026 PS 26264. No open-source license is granted yet; add one before any public release.
