# Ekasutra

**SIH 2026 · Problem Statement 26264** — an integrated institution complaint and coordination dashboard for AICTE.

> One institution. One thread. One owner. One proof.

Ekasutra joins every complaint about an institution — across the **Regulation Bureau (RB)** and the **Public Grievance Redressal Cell (PGRC)** — onto that institution's **AICTE Permanent ID**. Duplicate complaints become one owned case with a joint decision, a named lead bureau, and an append-only audit trail. Nothing is merged silently: every link is confirmed by a human.

**Build:** v8, cut 25 October 2026 · **Upload deadline:** 28 October 2026
**State:** prototype and submission documents complete · demo video **not recorded** · known evidence defects documented below.

---

## The problem

AICTE receives the same institution's problem through more than one window. RB sees approvals, inspections and compliance; PGRC sees student and staff grievances. The same college arrives with a different spelling, a different case number and a different clock. The institution is asked for the same documents twice, one bureau closes its file while the other is still open, and no single screen answers “who owns this institution right now?”

The problem statement asks for a single-window dashboard with eight capabilities: one view, current bureau, full movement, overlap detection, de-duplication, status monitoring, reports, and timeline alerts. Ekasutra implements all eight in the prototype.

## What v8 does

- **Identity resolution.** Permanent ID first, alias graph second, trigram similarity third. Exact Permanent ID wins; alias match is shown with evidence; fuzzy matches above the auto-link rule (score ≥ 92 and margin ≥ 8) link automatically, mid-band matches go to a human, everything else stays unmatched.
- **Collision check at intake.** Before a new case is created, the intake screen shows open cases at the same institution and forces a choice: link, joint case, or proceed with a written reason.
- **Overlap classes that mean something.** Duplicate, related, conflict and systemic are different states with different actions. A duplicate merges; a conflict escalates; a systemic pattern opens a room.
- **Coordination rooms.** One room per open overlap, with a lead bureau, named owners, activity timeline, joint decision, escalation reason, merge target and a printable one-page brief.
- **Custody and SLA.** Every case names its current bureau and officer, its next action, its age and whether it is beyond SLA. Custody is explicit, not inferred.
- **Append-only ledger.** Every action is written as `sha256(prev_hash ‖ UTC time ‖ actor ‖ action ‖ object)`. The browser and PostgreSQL can compute the same chain. A tamper-evident history is the accountability layer, not a log file.
- **Works offline.** The prototype is one HTML file, no server, no credentials, and opens from `file://` on a laptop or phone.

## Quick start

1. Open [`submission/Ekasutra_v8.html`](submission/Ekasutra_v8.html) in Chrome or Edge.
2. Click **90-sec tour** on the dashboard, or drive it manually:
   **Case Intake → Load sample → Resolve & check → Create joint case → Coordination Rooms → CR-01 → set lead bureau → joint decision → Escalate / Merge duplicate case / Export coordination brief → Audit Log → Verify chain.**
3. Reset from the profile menu (top-right avatar) → **Reset demo data**.

No install, no network, no API keys. State is stored in `localStorage` and survives reload until reset.

## Repository map

```
ekasutra/
├── submission/            the six upload artifacts, byte-for-byte
│   ├── Ekasutra_v8.html
│   ├── Ekasutra_SIH2026_SIH26264.pptx
│   ├── Ekasutra_SIH2026_SIH26264_preview.pdf
│   ├── Ekasutra_Data_Appendix.pdf
│   ├── Ekasutra_Submission_Kit.pdf
│   ├── Ekasutra_Database_Pack.zip
│   └── SHA256SUMS.txt
├── database/              the database pack, unpacked for review
│   ├── schema.sql         11 tables, register view, matcher, audit functions
│   ├── seed_demo.sql      deterministic demo seed (18 institutions, 32 cases)
│   ├── demo_seed.json     readable seed source
│   ├── generate_demo_seed.py
│   ├── seed_institutions.py
│   └── README.md          load, verify and API notes
├── docs/
│   ├── ARCHITECTURE.md    domain model, matching, ledger, target stack
│   ├── QA_REPORT.md       what passed, what is broken, evidence and grade
│   ├── DATA_NOTICE.md     what is real, what is synthetic, claim register
│   ├── SUBMISSION_CHECKLIST.md
│   ├── PS26264_MAPPING.md objective-by-objective mapping
│   ├── screenshots/       v8 QA captures (desktop, mobile, flows)
│   └── deck-preview/      one PNG per slide
├── qa/                    Playwright reproduction harness
├── CONTRIBUTING.md
├── CHANGELOG.md
└── README.md
```

## What is actually verified

Verified on 26 October 2026 against the files in this repository.

| Check | Result |
|---|---|
| Prototype opens offline from `file://`; nine screens navigate; console clean | Pass, no console or page errors at 1366×900 |
| Responsive layout | Pass at 360, 390, 768, 1024, 1366, 1920 px; **2 px overflow at 320 px** (open defect) |
| Intake → resolve → joint case → room decision → audit verify | Pass; chain reports 18 events after reset |
| Demo seed chain | Head `748b44fc1aad…fc6fe0`; independently recomputed, 0 broken links |
| Database model | 11 tables, constraints, `v_case_register`, `fn_match_institution`, seed guard |
| Deck | 6 slides, 16:9; preview PDF matches; embedded screenshots are v8 cream UI |
| Kit and appendix | 2 pages each, render checked |
| PS 26264 objectives | 8 of 8 mapped in the prototype (see `docs/PS26264_MAPPING.md`) |
| Demo video | **Not recorded** — blocking submission item |

**Not verified, and must not be claimed as built:** production API, authentication/RBAC, real file upload, concurrent write behaviour, national-scale matcher benchmark, and the 9,558-institution validation run. See `docs/QA_REPORT.md`.

## Read before presenting

Five defects can hurt a live demo or a judge review. Full detail and fixes are in [`docs/QA_REPORT.md`](docs/QA_REPORT.md).

1. **The browser “Verify chain” cannot detect tampering.** `renderAudit()` re-hashes the in-memory chain before comparing it, so an edited event is silently re-sealed and still reports “Chain intact”. Demonstrating tamper live will fail.
2. **The Data Layer header is stale after any action.** It always says “Newest entry · A-1054” while the displayed hash is live. The seeded DB also stays at 18 rows while the UI grows.
3. **Institution documents show three identical placeholder hashes.** The seed has 109 unique digests; the UI shows `9c2f4a7b` three times.
4. **The team slide lists seven roles** while SIH teams are six including the team lead, and the speaker notes say “six people”.
5. **Headline matcher numbers are not reproducible from the shipped pack.** The deck says 9,558 validated IDs, 2,726 variants, 95.0/98.2 and 100% precision at 70.3% coverage; the shipped appendix reports 367 variants at 94.6/99.7. No harness output or institutions CSV is in the repo.

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
