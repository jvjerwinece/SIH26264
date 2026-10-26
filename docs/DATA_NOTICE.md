# Data notice and claim register

**Applies to:** the prototype, screenshots, deck, kit, appendix and database seed in this repository.

Read this before recording the video, publishing screenshots, or sending the deck to anyone outside the team.

---

## 1. What is real

| Data | Source | Status |
|---|---|---|
| Institution names, cities, states, regions | Public AICTE institution listing | Real names, as published |
| AICTE Permanent ID format | AICTE scheme, `^[0-9]-[0-9]{6,10}$` | Real format |
| Problem statement text and objectives | SIH 2026 portal, PS 26264 | Real |
| PostgreSQL behaviour, hash formula, schema | Built and tested for this project | Real implementation |

The national master is **not** in this repository. `database/seed_institutions.py` can build a CSV from an AICTE list, but the list file is not shipped. The **9,558** figure is a master-count claim and cannot be reproduced from the current repo.

## 2. What is synthetic

Everything below was generated for the demo. None of it describes a real complaint, a real person, a real document, or a real decision.

| Data | Count in seed | Notes |
|---|---:|---|
| Institution rows | 18 | Real institution names, real-shaped Permanent IDs |
| Aliases | 27 | Invented spelling variants |
| Users | 9 | Invented officers; `@aicte.gov.in` addresses are illustrative |
| Cases | 32 | Invented complaints, categories, statuses and SLAs |
| Case events | 129 | Invented chronology |
| Documents | 109 | Invented filenames and SHA-256 digests |
| Overlap clusters | 3 | Invented duplicates/patterns |
| Overlap links | 7 | Invented |
| Rooms | 3 | Invented |
| Room activity | 5 | Invented |
| Audit entries | 18 | Deterministic demo chain |

No real student, faculty or institution staff personal data is present. No real grievance correspondence is present.

## 3. The reputational risk

The seed pairs **real institution names** with **fabricated complaints** — for example a scholarship-delay and laboratory-deficiency complaint against a named government polytechnic. In a private demo with a verbal caveat this is usually acceptable. In a public video, a public repository, or a deck forwarded without context, it can read as an allegation against a real college.

### Rules

1. **Label persistently.** Add a visible “Synthetic demo data” ribbon to the prototype shell, not only to the printable brief. Every screen that shows a case, document or person should carry it.
2. **Label illustrative identifiers.** The kit script uses Permanent ID `1-1234567`, which does not correspond to a seeded institution. Mark it “illustrative” on screen or replace it with a seeded ID.
3. **Anonymise for public artifacts.** For the video and any public repo, prefer “Institution A, Himachal Pradesh” over a real college name. Keep the real master in the private database.
4. **Never mix real and synthetic silently.** If a real complaint is ever added, it goes in a separate database with access control, retention policy and consent basis — never in this demo seed.
5. **Do not publish the national master.** Institution names are public; a joined view of names, complaints and officers is not.

## 4. Claim register

Use this table as the single source of truth for numbers. “Unsupported” means the shipped artifacts do not contain evidence sufficient to defend the claim to a judge.

| Claim | Where it appears | Status | What is actually supported | Action |
|---|---|---|---|---|
| “9,558 AICTE IDs” | Deck slide 1, preview cover, kit, appendix | **Master count, not a validation set** | 9,558 is the size of the institution master; the list is not shipped | Always say “master” or “IDs”; never “validated on 9,558” |
| 367 labelled name variants | Deck, preview, kit, appendix, prototype | **Supported as the evaluation size** | Appendix reports the run; harness output is not shipped | Keep; ship the variant set and output if a judge asks |
| 94.6% top-1, 99.7% top-3 | Deck, preview, kit, appendix, prototype | **Supported as reported** | Measured on 367 labelled variants | Keep; cite n = 367 |
| 0 silent merges | Deck, preview, kit, appendix | **Supported by design** | Auto-link is gated; everything else routes to a human | Keep |
| 2,726 variants, 95.0/98.2, 100% precision, 70.3% coverage, 322 duplicate names | Formerly deck and kit | **Withdrawn 27 October 2026** | No shipped artifact supports them | Do not reintroduce |
| 18 institutions, 32 cases, 109 documents, 18 audit rows | Appendix, DB pack | **Supported** | Deterministic seed | Keep |
| Chain head `748b44fc…fc6fe0` | Appendix, DB pack | **Supported** | Recomputed, 0 broken links | Keep |
| “Every action is tamper-evident” | Deck, tour | **Supported for the demo** | PostgreSQL chain is sound; the browser verifier now detects edited rows (P1-1 fixed) | Keep; fix P2-5 before real deployment |
| “Synthetic data labelled on every screen” | Formerly kit Q4 | **Removed** | The claim was false; documents now say the case data is synthetic without promising a label on every screen | Add the ribbon before recording |
| “Same code path in demo and production” | Formerly deck slide 3 | **Removed 27 October 2026** | Slide now separates the prototype (one HTML file) from the target stack | Keep the separation |
| Advisory text similarity (TF-IDF) | Prototype radar + intake, deck slide 3, kit Q3 | **Supported and demoable** | Cosine similarity over complaint narratives computed in-browser; threshold 0.30 across institutions, 0.20 at intake; never auto-links | Call it advisory; do not call it an LLM |
| Six-person team | Deck slide 6 | **Supported** | Lead 1, frontend + design 2, backend 2, data 1 | Keep |
| 3:00 video | Kit cover | **Not delivered** | No MP4 in archive; checklist says 2:50 | Record and verify duration |
| All eight PS objectives demoable | Deck, appendix | **Supported** | See `PS26264_MAPPING.md` | Keep |

## 5. If a judge asks for the data

The honest answer, in one breath:

> “The case data is synthetic and deterministic; 18 institutions, 32 cases, 109 documents and an 18-row audit chain. The institution master is public AICTE data, and the PostgreSQL schema and seed are in the pack. Our matcher evaluation is 367 labelled variants at 94.6% top-1 and 99.7% top-3, with zero silent merges; the larger harness is not part of this submission. On top of the rules, a TF-IDF text layer flags differently-worded complaints for an officer to review — advisory only, nothing auto-links.”

That answer is defensible, and it is now the answer every artifact gives.

## 6. Retention and access

- The demo runs locally in the browser; case state stays in `localStorage` until reset.
- The database pack is designed for a throwaway `ekasutra_demo` database. Do not load the demo seed into a database that holds real cases; the seed guard only protects against a non-empty target.
- Public artifacts should contain no officer emails, no real complainant names and no real case numbers.
