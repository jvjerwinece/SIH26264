# Changelog

All notable states of the submission. Earlier builds (v1–v7), earlier renders and the full archive are intentionally not part of this repository.

## [v8.2] — 2026-10-27

Advisory text-similarity layer, plus the production-stack relabel.

- **TF-IDF text similarity** over complaint narratives, computed in the browser with no model download: cosine ≥ 0.30 between active cases at different institutions surfaces a review pair on the Overlap Radar; cosine ≥ 0.20 against open cases elsewhere surfaces on the intake screen.
- **Extractive auto-brief** of the incoming complaint (sentence scoring, two sentences, subject line and greeting stripped).
- Every suggestion is advisory: *Review* opens the case, *Not related* logs a dismissal, and neither action links or merges anything.
- Deck slide 3 now separates prototype from target stack ("Prototype is one HTML file; the API is specified, not built") and lists TF-IDF as a matching signal; preview PDF page 3 patched to match. Closes P2-4.
- Kit Q3 ("Do you need an LLM / cloud?") rewritten to describe the rule core plus the TF-IDF assist.
- README, claim register, QA report and checklist updated with the new claim.

## [v8.1] — 2026-10-27

Remediation of the five P1 findings in `docs/QA_REPORT.md`, plus the P3 polish items.

- Audit verification is now a real tamper check: the chain is sealed once at load, appended without re-hashing, and verified against stored `prev`/`hash`. Editing a row and pressing **Verify chain** reports “Chain broken”.
- Data Layer shows the live newest audit ID and labels the psql comparison as the seeded 18-row snapshot.
- Institution documents render unique digests derived from `sha256(permanent_id | filename)`.
- Deck slide 6 reduced to six people (lead 1, frontend + design 2, backend 2, data 1) with matching notes.
- One numeric source everywhere: 9,558-ID master, 367 labelled variants, 94.6% top-1, 99.7% top-3, 0 silent merges. Removed 2,726 / 95.0 / 98.2 / 100% / 70.3% / 322 from the prototype, deck, preview PDF, kit and appendix.
- Deck preview PDF patched on pages 1, 4 and 6 to match the edited deck.
- Intake pluralisation, 320 px overflow, and the two unlabeled controls fixed.
- Checksums regenerated; Playwright QA re-run with no findings.

Still open: video, persistent synthetic ribbon, production-stack relabel, concurrent audit append.

## [v8] — 2026-10-25

Final submission build.

- Single-file offline prototype: dashboard, intake, overlap radar, coordination rooms, institutions, all cases, reports, audit log, data layer, institution profile.
- Identity resolution: Permanent ID, alias graph, trigram matching, human confirmation.
- Intake collision check with link / joint case / proceed-with-reason.
- Coordination rooms with lead bureau, joint decision, escalation reason, merge target, printable brief.
- Append-only audit chain mirrored in PostgreSQL; 18-row demo seed, head `748b44fc…fc6fe0`.
- PostgreSQL 14 pack: 11 tables, `v_case_register`, `fn_match_institution`, `audit_write`, `audit_verify`.
- Six-slide 16:9 deck, two-page data appendix, two-page submission kit, database pack.
- Responsive 360–1920 px; 320 px has a 2 px overflow on institution detail.

## [repo] — 2026-10-26

Clean handoff repository.

- Added `submission/` (six files + checksums), unpacked `database/`, v8 screenshots, deck previews.
- Added `docs/ARCHITECTURE.md`, `docs/QA_REPORT.md`, `docs/DATA_NOTICE.md`, `docs/SUBMISSION_CHECKLIST.md`, `docs/PS26264_MAPPING.md`.
- Added Playwright QA harness.
- No changes to the v8 submission files.

### Known issues at this tag

All five P1 issues below were fixed in v8.1.

- P1-1 browser audit verification re-seals tampered rows.
- P1-2 Data Layer newest-entry label and psql comparison go stale after actions.
- P1-3 institution documents show three identical placeholder hashes.
- P1-4 team slide lists seven roles; SIH teams are six.
- P1-5 headline matcher metrics are not reproducible from the shipped pack.
- P2-3 video not recorded.
- P2-4 production stack presented as built.
- P2-5 `audit_write()` chain append is not concurrency-safe.

See `docs/QA_REPORT.md` for evidence and fixes.
