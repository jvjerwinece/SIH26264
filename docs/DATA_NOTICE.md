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
| “Validated on 9,558 real AICTE Permanent IDs” | Deck slide 1 | **Misleading** | 9,558 is the master size; it is not a validation set and the list is not shipped | Reword to “9,558-ID master” and separate it from evaluation |
| 2,726 name variants | Deck slide 4, kit | **Unsupported** | Appendix evaluates 367 variants | Drop, or ship the variant set and harness output |
| 95.0% top-1, 98.2% top-3 | Deck slide 4, kit | **Unsupported** | Appendix reports 94.6% / 99.7% on 367 variants | Use 94.6 / 99.7 and state n = 367 |
| 100% precision on high-confidence auto-links | Deck slide 4 | **Unsupported** | No labelled precision run shipped | Drop unless the harness and labels are shipped |
| 70.3% coverage | Deck slide 4, kit | **Unsupported** | No coverage run shipped | Drop with the precision claim |
| “100% auto-link coverage at 100% precision” | Kit evidence line | **False / contradictory** | Contradicts the deck's 70.3% coverage | Delete; replace with the appendix figures |
| 322 duplicate canonical names | Deck slide 4 | **Unsupported** | Not computed in any shipped artifact | Remove until computed and reproducible |
| 18 institutions, 32 cases, 109 documents, 18 audit rows | Appendix, DB pack | **Supported** | Deterministic seed | Keep |
| Chain head `748b44fc…fc6fe0` | Appendix, DB pack | **Supported** | Recomputed, 0 broken links | Keep |
| “Every action is tamper-evident” | Deck, tour | **Partially supported** | PostgreSQL chain is sound; browser verifier re-seals edits (P1-1) | Fix P1-1 or qualify the claim |
| “Synthetic data labelled on every screen” | Kit Q4 | **False** | Only the brief footer is labelled | Add ribbon or correct the answer |
| “Same code path in demo and production” | Deck slide 3 | **False** | Prototype is static HTML; no API/auth/DB connection | Relabel as target stack |
| Six-person team | Deck notes | **Contradicted** | Slide lists seven roles | Consolidate to six |
| 3:00 video | Kit cover | **Not delivered** | No MP4 in archive; checklist says 2:50 | Record and verify duration |
| All eight PS objectives demoable | Deck, appendix | **Supported** | See `PS26264_MAPPING.md` | Keep |

## 5. If a judge asks for the data

The honest answer, in one breath:

> “The case data is synthetic and deterministic; 18 institutions, 32 cases, 109 documents and an 18-row audit chain. The institution master is public AICTE data, and the PostgreSQL schema and seed are in the pack. Our matcher evaluation is 367 labelled variants at 94.6% top-1 and 99.7% top-3; the larger harness is not part of this submission.”

That answer is defensible. The current slide-4 numbers are not.

## 6. Retention and access

- The demo runs locally in the browser; case state stays in `localStorage` until reset.
- The database pack is designed for a throwaway `ekasutra_demo` database. Do not load the demo seed into a database that holds real cases; the seed guard only protects against a non-empty target.
- Public artifacts should contain no officer emails, no real complainant names and no real case numbers.
