# Changelog

All notable states of the submission. Earlier builds (v1–v7), earlier renders and the full archive are intentionally not part of this repository.

## [v9.4] — 2026-10-29

The prototype gets a real three-tier demo stack: dashboard on Vercel, FastAPI on Render, PostgreSQL on Supabase. Local end-to-end verified; cloud projects not yet provisioned.

- **FastAPI service, not a mock.** `server/app.py` exposes bootstrap, meta, audit, verify, matcher, case creation, case actions, overlap dismissal and room actions. Every write is one transaction: ledger change + `case_events` row + `audit_write()`. The actor is resolved server-side from `X-Demo-Role` against seeded users; the request body cannot name an actor.
- **PostgreSQL pool built for a pooler.** `server/db.py` uses psycopg3 with `prepare_threshold=None` (Supavisor-compatible), a checkout `select 1` probe with one retry, and `max_idle=120`. A dropped database no longer turns into a 500 on the next request.
- **Audit chain is concurrency-safe.** `audit_write()` takes `pg_advisory_xact_lock(hashtext('ekasutra.audit_chain'))` and `audit_entries_prev` is unique on `prev_hash`. Parallel-writer test: 20 writers, 18 → 38 rows, 38 distinct predecessors, 0 duplicates, verify ok. Seed head stays `748b44fc…fc6fe0`.
- **The dashboard runs live.** `web/index.html` is derived from the frozen submission file and adds `connectLive()`: seed renders first, `/api/bootstrap` replaces it, writes are API-first and re-hydrate from PostgreSQL. `file://` and unreachable APIs keep the offline seed and say so. Footer reads `Live · Supabase + Render`; Data Layer gained a live card and a “Verify chain in PostgreSQL” button.
- **Counts are read, not estimated.** The Data Layer previously computed `case_events` as `cases × 4 + 1` (133) while SQL held 130. Aliases, users, documents and events now use `/api/meta` counts; the E2E screen matched SQL row-for-row.
- **No toast outruns the database.** Intake “Proceed with reason” now posts the override to `/api/cases`; link/joint no longer claim an audit write that never happened. `reopen` is a real event kind, not a `note`.
- **Deployment configs.** `render.yaml` (Docker, `server/`, `/health`, free plan, Singapore), `web/vercel.json` (`sin1`, security headers), `web/api/[...path].js` (same-origin proxy to Render with path validation), `server/.dockerignore`, `.env.example`, and a step-by-step `docs/DEPLOYMENT.md` covering Supabase SQL, connection pooling, the Vercel root directory, custom-domain DNS and demo reset.
- **Supabase bundles.** `tools/build_supabase_bundle.py` now writes both `Ekasutra_Supabase.sql` (fresh project) and `Ekasutra_Supabase_Reset.sql` (truncate + reseed), each ending in a verification row. The reset bundle was loaded on PostgreSQL 16: 32 cases, 18 audit rows, chain ok, unchanged head.
- **Docs corrected against the current seed.** The matcher example was still quoting a 58.4 runner-up from an older seed; it is 67.2 (25.5-point margin) today, and `ARCHITECTURE.md` §2/§7/§8/§9 now describe the built stack instead of the old target. README, QA report and claim register keep hosted URLs, auth and uploads in the “not built” list.

Verified locally on 29 October 2026: PostgreSQL 16.15 + FastAPI + Chromium; create `C-2026-0199`, dispose as `R. Menon`, reopen as `P. Rao`, audit 18 → 21, Data Layer `33 cases / 130 events / 19 audit rows`, PostgreSQL chain verification, proxy harness 5/5, clean reset to the seeded head. **Not done:** cloud projects and DNS, login/RBAC, real uploads, video.

## [v9.3] — 2026-10-28

Page 3's discs are optically centred, and the tech-stack strip now states what ships.

- **A/B/C were sitting 16 % low in their circles.** Segoe MDL2 Assets has no Latin letters, so those three runs were silently falling back to Arial — and PowerPoint centres the line box, not the glyph ink, so every disc rendered 0.9–2.5 pt below centre. `disc()` now takes a measured `lift` (icons 1.3 px, letters 1.05 px) and a horizontal nudge; all thirteen discs plus the two new lane discs now measure within ±0.62 pt of centre in the exported PDF.
- **The glyph has to live in a shape, not a textbox.** Routed through `add_textbox`, PowerPoint exported the symbol glyphs with a missing-glyph box (the 8.5 pt lane icons came out as dots) and `spAutoFit` moved the letters again. The label now rides in an unfilled oval offset by `lift`; the filled disc stays exactly where it was drawn.
- **The stack strip is two lanes, not one row.** "Runs today, in this pack" (check disc, solid pills) is separated by a hairline from "Pilot build — not built yet" (warning disc, dashed pills in muted ink). Before this, all eight pills looked identical apart from a 10 pt caption, which read as if Next.js and FastAPI shipped.
- **Verified from the export.** Letter and icon offsets measured on every disc, nothing re-wrapped, text scan unchanged (0 retired figures, 2× 9,558, 4× 367, 2× 94.6, 2× 99.7), 6 pages at 960×540 pt, checksums regenerated and verified.

## [v9.2] — 2026-10-28

The prototype is legible from a projector, and the deck carries captures of that build.

- **Type floor.** Site labels sat at 7.5–9 px. One CSS block raises everything under 10.5 px to 9–9.5 px (`th`, `label`, nav labels, table headers, chips, hashes, case IDs) and leaves every size above that alone. Nothing was restyled beyond the small text; body copy stays 13 px.
- **Evidence chips were run together.** Adjacent chips in the overlap card rendered as `…PERMANENT ID● ALIAS MATCHED…` because the container had no gap. `.why` is now a wrapping flex row with a 14 px column gap, so each chip's dot reads as its own bullet.
- **Measured, not eyeballed.** A Playwright pass over five views reports no text node below 8.5 px except the version badge, and `scrollWidth` never exceeds the viewport at 1440. The QA flow re-ran after the change: 9 views, 0 console errors, 0 overflow at 320–1920 px, a11y 0/0/0.
- **Captures re-shot from this build** and re-cropped against measured element boxes rather than guessed coordinates: `dash_main.png` 1136×710, `reports_band.png` 2272×1212, `radar_card.png` 1576×562. Deck rebuilt, PDF re-exported (6 pages, 960×540 pt), claim scan unchanged.

## [v9.1] — 2026-10-28

Page 3 becomes a pictorial flowchart: the same tree, but every step now carries an icon, so the diagram reads before the text does.

- **Icons in the tree.** All nine step cards on page 3 gain a tinted disc with a thin-line glyph from Segoe MDL2 Assets — ID card, magnifier, person for branch A; ranked list, check, return arrow for B; page, stack, question mark for C. The three branch tabs get filled letter discs (A/B/C), the entry chip a warning disc, the decision box a search disc, and each outcome card a solid colour disc (check / person / shield).
- **Still native and editable.** Every disc is an oval plus a glyph run, so the file stays text and shapes. The glyph font is embedded in the PDF as a subset (`ABCDEE+Segoe MDL2 Assets`), so the icons render on a machine that has never seen the font. The deck does not depend on an image for the flowchart.
- **Copy tightened where the icons took width.** "Nothing merges without a named officer." became "No merge without a named officer." and the queue sub-line became "queued for the data team to approve", because both wrapped into the next card. The decision question drops to 16.5 pt so it stays on one line beside its disc.
- **Verified from the export, not the source.** Every node label and sub-line measured inside its 44 px card, no span crossing a card edge, all six pages re-rendered and read. Text scan unchanged: 0 retired figures, 2× 9,558, 4× 367, 2× 94.6, 2× 99.7, 6 pages at 960×540 pt.

## [v9] — 2026-10-28

The portal deck is rebuilt against the winning sample: bigger type, a capture on four of six pages, and a real decision tree instead of a card snake.

- **Type and spacing.** Section titles are 38 pt Times New Roman bold with light tracking, body is 15 pt Arial, captions 12.5 pt. The average body size of the previous deck was 9.5–12 pt; the winning sample ran 20–32 pt. Every grey "one · two · three" middot strip is gone — each block is one written paragraph, and the only middot lines left are data labels.
- **Page 1** keeps the template layout and the bulb art, and gains a single thesis line under the metadata. The Team ID stays an amber `[ add from SIH portal ]` placeholder on purpose.
- **Page 2** carries the dashboard capture at 506×316, a three-step strip and one seeded case: three cases about Vidyasagara College of Engineering that arrived under different spellings, two sitting with PGRC and one with RB — `C-2026-0142` / `C-2026-0198` vs `C-2026-0167` in `database/demo_seed.json`.
- **Page 3** is a native three-branch decision tree, all shapes and editable text: complaint → "do we already know this institution?" → A exact ID or alias, B fuzzy ranked candidates, C not in the master. Each branch is a dashed frame of three steps ending in one rule, and a run-today / target stack strip closes the page. No raster flowchart is needed.
- **Page 4** keeps five measured tiles, three feasibility lines, five "what can break, what we do" cards and the six-week pilot.
- **Page 5** uses a reports capture re-shot with the dev ribbon hidden, the eight PS objectives against what the prototype shows, and SOCIAL / ECONOMIC / GOVERNANCE cards plus an environmental line — the template asks for social, economic and environmental benefits, so all three are now named.
- **Page 6** holds six sources, a fresh radar capture, three evidence chips (18 audit events, SHA-256 chain intact, 0 silent merges) and the data-access note.
- **Claims unchanged and re-scanned:** 2× 9,558, 4× 367, 2× 94.6, 2× 99.7, 1× 18 audit events, 1× 11 tables, 0 occurrences of every retired figure. PDF is 6 pages at 960×540 pt.
- **Synthetic data:** every capture in this deck shows fictional institutions only; the four reshoots came from the renamed seed.

## [v8.7] — 2026-10-27

The portal deck now carries real product screenshots instead of only native shapes.

- **Three live captures from the prototype** (`qa/qa_flow.js`, 1366×900 Playwright runs) ship in `submission/media/` and sit in the deck: the dashboard command centre on page 2 (hero, under the three flow rows) and the overlap radar plus the audit chain side by side inside the page-6 evidence card. No stock photography — every image is this prototype, which is what the winning decks' Figma mocks are not.
- **Page 2 rebuilt around the capture**: the three flow steps became compact single-row cards (bureau colours kept on step 03) so the dashboard gets a 495×248 band; an amber "PROTOTYPE V8 · SYNTHETIC DATA" badge sits on the image corner, aspect-correct via picture crops, 1 pt border.
- **Page 6 evidence card** grew from 260 to 352 px tall: two 218×170 thumbs with captions ("98% match, officer confirms" / "18 events · SHA-256 intact"), three condensed evidence lines and the unchanged DATA ACCESS note. The synthetic-data line the thumbs replace is now visible in them: the capture carries the new ribbon.
- **P2-1 half-closed**: a persistent amber ribbon ("SYNTHETIC DEMO DATA · NO REAL COMPLAINANTS") is fixed to the bottom-right of every prototype view, so any capture — deck, video, screenshots — is self-labelling. Anonymising the institution names in public captures stays open.
- Full QA re-run after the HTML edit: 9 views, 0 console errors, intake collision, joint room, tamper detected, 4/4 unique digests, all widths, a11y 0/0/0. Bounds check clean; PDF text scan unchanged (retired 0; 4× 9,558, 7× 367, 2× 94.6, 2× 99.7). Checksums regenerated for all eight artifacts, including the previously stale `Ekasutra_v8.html`.

## [v8.6] — 2026-10-27

The portal deck closes the visual gap against the winning decks we compared it with.

- **Page 5 gained a status-quo vs Ekasutra table** (8 capability rows, deep-blue header, alternating rows, red ✗ under TODAY, green ✓ under EKASUTRA) in place of the three bullet columns. Every row is demoable in the prototype; the one modelled figure (officer-days) is flagged in a footnote under the table. The seed chart moved to the top-left and the three measured stat cards run across the bottom.
- **Page 3 got lane colours and stage icons**: RB deep-blue, PGRC blue, regional office green — the same three colours as the chart legend on page 5 and the bureau names on page 2 — with each intake arrow taking its lane colour, and a glyph per stage (◎ resolve, ① thread, ∩ overlap, ⇄ coordinate, ▦ register, ∑ audit). All native shapes and text; no image assets.
- **Page 2 colours the three bureaus** in the step-03 subtitle to match.
- Two glyphs did not survive the first render (⛓ showed as tofu, ① at 11.5 pt wrapped the THREAD card) and were swapped for ∑ and tighter spacing; every page re-rendered from the PowerPoint export afterwards.
- Bounds check: no shape off the 1280×720 canvas. PDF text scan: retired figures still 0; 4× 9,558, 7× 367, 2× 94.6, 2× 99.7 unchanged. Checksums regenerated.

## [v8.5] — 2026-10-27

Official deck rebuilt to carry real diagrams instead of three-column bullet lists.

- **Page 3 gained a system-flow diagram** in place of the six-card snake: three intake channels (RB, PGRC, regional office) converge on `01 RESOLVE`, then `02 THREAD` → the `0 silent merges` tile → `03 OVERLAP` → `04 COORDINATE` → `05 REGISTER`, with `06 AUDIT CHAIN` and its `sha256(prev || time || actor || action || object)` formula below. All native shapes and arrows, no image assets, so the file stays editable and the PDF stays small. The duplicated hash line in the left column is gone.
- **Page 5 gained a bar chart** drawn from the shipped seed: PGRC/RB complaint counts per institution for the three overlap clusters, each collapsing to one thread (`CL-01 · 3 files`, `CL-02 · 2 files`, `CL-03 · 2 files`). Every bar length is a count in `database/seed_demo.sql`; the caption says so. The "7 → 3" stat card it replaces is now shown rather than asserted.
- Density, counted in the exported file: 44 shapes on page 3 and 48 on page 5, against 8–21 on the rest — the two pages a judge scores on "how does it actually work" now carry the graphics.
- Re-rendered pages 1, 3 and 5 from the PowerPoint export and checked for overflow: no shape leaves the 1280×720 canvas, the chart caption fits on one line inside its card. PDF is 6 pages, 960×540 pt; retired figures still zero.

## [v8.4] — 2026-10-27

Official deck audited against the per-slide traps a judge actually reads for.

- **Page 2 now names one real case** instead of a description that would survive swapping the regulator: three fee, scholarship and intake complaints about Vidyasagara College of Engineering, Kanchipuram — three name spellings, two in PGRC, one in RB. Taken from the shipped seed, so a jury member can load it and count.
- **Page 3 splits the stack into RUNNING TODAY and TO BUILD.** Green rows are checkable now (one HTML file, Web Crypto SHA-256 chain, PostgreSQL 16 schema + 18-row seed loading in psql); blue rows are declared as not built. The previous single list read as a stack nobody had run.
- **Page 4 becomes five "what can break → what we do" cards** covering wrong match, data we cannot ship, adoption, audit concurrency and security — the questions a jury asks out loud, with the two open gaps still stated plainly.
- **Page 5 gains a second measured number:** 7 → 3. Seven seeded complaints about three institutions, every overlap spanning RB and PGRC. The officer-day model stays labelled as a model.
- **Page 6 adds the data-access answer** (institution master is public AICTE data, not redistributed in this pack; the 367-variant set is ours and ships) and a sixth named source for the intake channels.
- Both the technical-approach and references strips now say the demo has no host to time out — no cold start in front of a jury.
- Re-exported PDF: 6 pages, 960×540 pt, retired figures still zero.

## [v8.3] — 2026-10-27

Idea deck rebuilt on the official SIH 2026 template, plus a real PPTX→PDF path.

- **`Ekasutra_SIH2026_SIH26264_Official.pptx`** is now the portal upload: built directly inside the downloaded `SIH2026-IDEA-Presentation-Format.pptx`, keeping its header, logo, team oval and blue footer, filling the five required sections and deleting only the instructions slide. Six slides, the allowed maximum.
- Structure borrowed from three winning SIH idea decks the team collected (dense infographic blocks, explicit flow, risk column, references page). Only the structure was taken; none of their content, and the official section list is what the layout follows.
- **`Ekasutra_SIH2026_SIH26264_Official.pdf`** exported through PowerPoint COM, so the portal-required PDF is reproducible from source instead of hand-patched. The builder, the exporter and an unmodified copy of the official template now live in `tools/`; `python tools/build_official_deck.py` regenerates the deck from scratch.
- Same claim register as every other artifact: 9,558 Permanent IDs, 367 labelled variants, 94.6% top-1, 99.7% top-3, 0 silent merges; the officer-day saving is labelled "Modelled"; RBAC and concurrent audit writes are shown as not built.
- One field is deliberately left blank: **portal Team ID** on page 1, shown in amber. Fill it, then re-export the PDF.
- The previous deck stays in the pack as the long-form version; README and checklist now name both.

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
