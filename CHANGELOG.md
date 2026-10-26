# Changelog

All notable states of the submission. Earlier builds (v1–v7), earlier renders and the full archive are intentionally not part of this repository.

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

- P1-1 browser audit verification re-seals tampered rows.
- P1-2 Data Layer newest-entry label and psql comparison go stale after actions.
- P1-3 institution documents show three identical placeholder hashes.
- P1-4 team slide lists seven roles; SIH teams are six.
- P1-5 headline matcher metrics are not reproducible from the shipped pack.
- P2-3 video not recorded.
- P2-4 production stack presented as built.
- P2-5 `audit_write()` chain append is not concurrency-safe.

See `docs/QA_REPORT.md` for evidence and fixes.
