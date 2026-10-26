# QA report — Ekasutra v8

**Build:** v8, cut 25 October 2026
**Audit date:** 26 October 2026
**Remediation and re-verification:** 27 October 2026
**Auditor:** internal pre-submission review
**Scope:** `submission/` (HTML, PPTX, preview PDF, appendix, kit, database pack), `database/` source, deck and kit renders.

**Verdict (26 October):** a strong, coherent prototype with an unusually good domain model, held back by claim-integrity defects in the submission layer. The build is credible in a live demo until a judge tests the audit claim or asks for the matcher harness. Fix the five P1 items before 28 October.

**Status (27 October):** P1-1 to P1-5, P3-1, P3-2 and P3-3 are fixed and re-tested. The prototype, deck, preview PDF, kit and appendix now carry one set of matcher numbers. Remaining blockers are the unrecorded video and the production-stack caveats listed in §8.

---

## 1. Score

Scores are as of the 26 October audit; the right-hand column records the 27 October remediation.

| Dimension | Weight | Score | After fixes | Why |
|---|---:|---:|---:|---|
| Problem fit and insight | 15% | 9.0 | 9.0 | Institution-first model, overlap classes, custody and coordination rooms map directly to PS 26264 |
| Prototype completeness | 25% | 9.0 | 9.5 | All eight objectives are demoable; intake-to-audit flow closes; responsive and offline; audit and stale-label defects fixed |
| Technical depth | 20% | 8.5 | 8.5 | Real schema, register view, trigram matcher, hash chain, constraints; production layer not built |
| Evidence and claim integrity | 20% | 6.5 | 9.0 | Numbers now agree across all artifacts; tamper check detects edits; document digests unique. Harness output and the 9,558-row list are still not shipped |
| Submission readiness | 10% | 7.5 | 8.0 | Deck, kit, preview and appendix aligned and team slide fixed; video still missing |
| Design and polish | 10% | 8.5 | 9.0 | Clear editorial visual language; 320 px overflow and unnamed controls fixed |
| **Weighted total** | **100%** | **8.2 / 10** | **8.9 / 10** | |

Recording the video and relabelling the production stack as a plan would move this to roughly **9.3**. The model itself does not need rescuing.

## 2. Method and reproduction

- Manual walkthrough of every screen at 1366×900 and at 320/360/390/768/1024/1366/1920 px.
- Scripted flow: intake → resolve → joint case → room decision → audit verify → reload → reset.
- Tamper probe: modify the newest audit row in memory, re-render the audit screen, press **Verify chain**.
- Independent recomputation of the 18-row seed chain from `database/seed_demo.sql`.
- Cross-read of deck, preview PDF, appendix, kit and database pack for numeric and factual consistency.
- Playwright harness included at [`qa/qa_flow.js`](../qa/qa_flow.js); see [`qa/README.md`](../qa/README.md).

Commands:

```bash
cd qa
npm install
npx playwright install chromium      # or use installed Edge
node qa_flow.js
```

## 3. Verified passes

| # | Check | Evidence | Result |
|---|---|---|---|
| V1 | Opens offline from `file://`, no server | Chrome/Edge, network disabled | Pass |
| V2 | Nine screens navigate without console or page errors | 1366×900, console listener | Pass, 0 errors |
| V3 | Intake sample resolves and offers link / joint / override | Load sample → Resolve & check | Pass |
| V4 | Joint case creation and room decision | CR-01, lead bureau, joint decision | Pass |
| V5 | Audit screen reports 18 events after reset | Verify chain | Pass — but see P1-1 |
| V6 | Persistence across reload; reset restores seed | Merge + escalate survive reload | Pass |
| V7 | Responsive layout, no horizontal overflow | 360, 390, 768, 1024, 1366, 1920 px | Pass |
| V8 | Database model loads and is internally consistent | 11 tables, constraints, view, matcher, 18-row seed | Pass by inspection and independent chain recomputation |
| V9 | Seed chain head | `748b44fc1aad8e9a1c05d0040b54e95f68d966ea5396dffc789139aab9fc6fe0` | Pass, 0 broken links |
| V10 | Deck shape (long-form) | 6 slides, 16:9, preview PDF matches | Pass |
| V11 | Deck screenshots are current v8 cream UI | Extracted PPTX media | Pass |
| V12 | Kit and appendix pagination | 2 pages each, render checked | Pass |
| V13 | PS 26264 objectives | 8 of 8 mapped | Pass — see `PS26264_MAPPING.md` |
| V14 | Official-template deck | Built inside the downloaded SIH 2026 Idea format; 6 slides; instructions slide deleted; header, logo, team oval and footer preserved; PDF exported from PowerPoint, 6 pages at 960×540 pt | Pass |
| V15 | Official-template deck claim audit | Text extracted from the exported PDF: 2,726 / 95.0 / 98.2 / 100% / 70.3 / 322 / 22% / “labelled on every screen” / “same code path” all 0 occurrences; 9,558 × 3, 367 × 4, 94.6 × 2, 99.7 × 2 | Pass |

## 4. Findings

### P1-1 · Browser “Verify chain” cannot detect tampering

**Status:** Fixed 27 October 2026 — see §7.

**Where:** [`Ekasutra_v8.html`](../submission/Ekasutra_v8.html) line 1402 `rehashAudit()`, called by `renderAudit()` at 1571 and `applyState()` at 1406; comparison at 1577.

**Evidence:** changing `audit[0].action` to `TAMPERED ACTION` and re-rendering changed the head hash from `748b44fc1aad…` to `5933b1db0318…`, and **Verify chain still returned “Chain intact · 18 events”**. The recomputation re-seals the edited row before comparing.

**Why it matters:** the tour's fifth stop and the deck's “Proof, not promises” claim invite a judge to test this. A judge who edits a row — or simply asks how tampering is detected — exposes that the browser check is an integrity check, not a tamper check.
**Fix:** store the chain once at load and verify the **stored** `prev`/`hash` against recomputation without mutating them. Only recompute on a legitimate append. Optionally ship a seeded chain with a known-good head and compare against it. Do not call `rehashAudit()` from any render path.

### P1-2 · Data Layer header and DB comparison go stale after any action

**Status:** Fixed 27 October 2026 — see §7.

**Where:** header hardcoded “Newest entry · A-1054” at line 1620; hash value computed from live `audit` around 1587.

**Evidence:** after `addAudit('QA probe action', …)`, the screen still read “Newest entry · A-1054” while the displayed hash was `134db76e…`. The seeded database remains at 18 rows and head `748b44fc…`, so the comparison the screen instructs the judge to run in psql will not match.

**Why it matters:** the Data Layer is the strongest technical screen. It currently fails the one check it asks the judge to perform, after any interaction in the demo.
**Fix:** render the ID from `audit[0].id`; either show the DB comparison only against the untouched seed (with a “seeded snapshot” caption) or reseed the database after actions. Add a “reset to compare with psql” action on the screen.

### P1-3 · Institution documents show placeholder hashes

**Status:** Fixed 27 October 2026 — see §7.

**Where:** line 1347; four documents map to `(k ? '9c2f4a7b' : '4a8e1d3c')`.

**Evidence:** institution detail renders `4a8e1d3c`, `9c2f4a7b`, `9c2f4a7b`, `9c2f4a7b`. The seed contains **109 documents with 109 unique 64-character digests**, none beginning `9c2f4a7b`.

**Why it matters:** the card says “Every document is hashed on upload”. Three different files sharing one 8-character digest is a visible contradiction on a screen a judge is likely to open.
**Fix:** render a real digest per seeded document (truncated display is fine), or derive a display hash from `case id + filename` until document data is wired to the UI.

### P1-4 · Team slide lists seven roles; SIH teams are six

**Status:** Fixed 27 October 2026 — see §7.

**Where:** `submission/Ekasutra_SIH2026_SIH26264.pptx`, slide 6.

**Evidence:** Team Lead 1, Frontend 2, Backend 2, Data 1, Design/Video 1 = **7**. Speaker notes say “We are six people” and then enumerate seven roles.

**Why it matters:** team size is an eligibility rule (six including the team lead). An evaluator counting the slide gets a contradiction before hearing the idea.
**Fix:** consolidate to six — e.g. Lead (1), Frontend + design/video (2), Backend (2), Data/QA (1) — and make the notes match the slide and the actual team.

### P1-5 · Headline matcher metrics are not reproducible from the shipped pack

**Status:** Fixed 27 October 2026 — see §7.

**Where:** slide 1 (“validated on 9,558 real AICTE Permanent IDs”), slide 4 (9,558 / 2,726 / 95.0% / 98.2% / 100% / 322 duplicate names / 70.3% coverage), kit (100% precision at 70.3%), appendix (367 variants at 94.6% / 99.7%).

**Evidence:**

- The appendix evaluates **367** generated variants at **94.6% top-1 / 99.7% top-3**, and explicitly says the 95.0/98.2 figures come from a wider harness that is **not shipped**.
- The database pack can generate a 9,558-row institutions CSV, but the source AICTE list, the 2,726-variant set, the 322 duplicate-name count and any harness output are **not in the repository**.
- 9,558 is the size of the institution master, not a validation set. “Validated on 9,558” conflates the two.
- The kit's “100% auto-link coverage at 100% precision” contradicts the deck's “100% precision at 70.3% coverage” and cannot both be true.

**Why it matters:** this is the first thing a technical judge will probe. An unsupported 100% precision claim converts a strong prototype into a credibility problem.
**Fix:** pick one source of truth. Either ship the variant set, the 9,558 CSV and the harness output, or restate the deck as “367 labelled variants: 94.6% top-1, 99.7% top-3; 9,558-ID master loaded” and drop 2,726, 95.0/98.2, 100%, 70.3% and 322 until the harness is shipped.

### P2-1 · Real institution names paired with fabricated complaints

**Where:** deck, kit and screenshots (e.g. “Government Polytechnic, Kangra” with a fabricated laboratory/scholarship complaint); illustrative Permanent ID `1-1234567` in the kit script.

**Why it matters:** the institution names are real; the allegations are invented. Presented publicly without a persistent label, this can read as a real accusation against a named college. The ID is valid-shaped but not tied to a seeded record.
**Fix:** add a visible “synthetic demo” ribbon on every screen and every slide that shows case content; label illustrative IDs; consider anonymising institution names in public screenshots (“Institution A, Himachal Pradesh”) while keeping the real master in the database.

### P2-2 · “Synthetic and labelled on every screen” is false

**Where:** kit Q4.

**Evidence:** the prototype has no persistent synthetic-data label. Only the printable brief footer says “seeded demo data”; the dashboard and case screens do not.

**Fix:** either add the ribbon (preferred) or correct the answer to “synthetic data, labelled in the brief and the submission documents”.

### P2-3 · Video is missing and duration is inconsistent

**Where:** kit cover says “Video: 3:00”; kit checklist says “Rehearse to 2:50”; no MP4 in the archive.

**Why it matters:** the video is a scored submission artifact. A missing file is a zero for that component regardless of prototype quality.
**Fix:** record a 2:50 cut, 1920×1080, H.264 MP4, clear audio, no copyrighted music, and verify duration and playback on a phone before upload. Follow the shot list in `SUBMISSION_CHECKLIST.md`.

### P2-4 · “Same code path in demo and production” is not true

**Status:** Fixed 27 October 2026 — slide 3 now labels the stack “TARGET STACK” and states “Prototype is one HTML file; the API is specified, not built.” Preview page 3 patched to match.

**Where:** slide 3, with “Next.js · FastAPI · PostgreSQL · Docker”.

**Evidence:** the prototype is static HTML with in-memory arrays and `localStorage`. There is no API, no auth, no database connection and no Docker image in the repository.

**Why it matters:** a judge who asks to see the API or the container will find neither. The target stack is a reasonable plan; presenting it as built is not.
**Fix:** relabel as “Prototype: single-file HTML. Target stack: Next.js, FastAPI, PostgreSQL, Docker — API contract defined, not yet implemented.” Keep the architecture slide; remove the equivalence claim.

### P2-5 · `audit_write()` can fork the chain under concurrency

**Where:** [`schema.sql`](../database/schema.sql) lines 177–198.

**Evidence:** `select hash into v_prev from audit_entries order by id desc limit 1;` takes no lock. Two concurrent transactions can read the same predecessor and insert two children.

**Why it matters:** the central “tamper-evident” claim depends on a single chain. A fork is not detected by a linear verifier.
**Fix:** serialise appends with `pg_advisory_xact_lock(<constant>)` or a chain-head row selected `for update`; add a unique index on `prev_hash` (genesis excepted) to make a fork fail loudly.

### P3-1 · Intake grammar

**Where:** line 1204: `open.length + ' open cases already exist'`.

**Evidence:** with one open case the banner reads “1 open cases already exist”.
**Fix:** pluralise (`open.length === 1 ? 'case' : 'cases'`).

### P3-2 · 2 px horizontal overflow at 320 px on institution detail

**Where:** institution detail screen, status chip.

**Evidence:** `document.scrollWidth = 322`, `clientWidth = 320`; the `.chip.blue` element ends at 321.5 px. Other screens and widths are clean.
**Fix:** allow the chip to shrink or wrap at ≤340 px, or reduce horizontal padding on the header row.

### P3-3 · Minor accessibility gaps

**Evidence:** one unnamed button (`Audit log` bell, icon-only), one unlabeled control (`#roleSelect`), no missing image alts. No formal axe run was performed.
**Fix:** add `aria-label="Audit log"` to the bell and a visually hidden `<label for="roleSelect">`; run axe before any public deployment.

### P3-4 · Appendix/deck/kit numeric drift

**Where:** appendix 367 variants at 94.6/99.7; deck 2,726 at 95.0/98.2; kit 100% at 70.3%.

**Fix:** one claims table, one harness output, one set of numbers across all artifacts. The claim register in `DATA_NOTICE.md` is the working source.

## 5. Cross-artifact consistency

State after the 27 October remediation:

| Claim | Deck | Kit | Appendix | Database pack | Status |
|---|---|---|---|---|---|
| 9,558 institution master | Yes (“9,558 AICTE IDs”) | Yes | Yes | Generator can build it; source list absent | Consistent; master list not shipped |
| 367 labelled variants | Yes | Yes | Yes | No | Consistent; harness output not shipped |
| 94.6% top-1 / 99.7% top-3 | Yes | Yes | Yes | No | Consistent; harness output not shipped |
| 0 silent merges | Yes | Yes | Yes | Yes (constraints + audit) | Supported by design |
| 100% precision / 70.3% coverage | Removed | Removed | Removed | — | Withdrawn |
| 322 duplicate canonical names | Removed | — | — | — | Withdrawn |
| 18 institutions / 32 cases / 109 docs / 18 audit rows | — | — | Yes | Yes | Supported |
| Chain head `748b44fc…` | — | — | Yes | Yes | Supported |
| Six-person team | Yes | — | — | — | Consistent |
| Video 3:00 | — | Cover 3:00, checklist 2:50 | — | — | Missing |
| Same code path demo/production | No (target stack labelled) | — | — | No | Resolved — P2-4 fixed |
| Advisory text similarity (TF-IDF) | Yes | Yes (Q3) | — | — | Supported — demoable |

The prototype’s Radar screen, the deck, the preview PDF, the kit and the appendix all read 9,558 / 367 / 94.6% / 99.7% / 0. The HTML was the last stale surface and was corrected in the same pass. The official-template deck added on 27 October was audited against the same five rows and carries no new number; the retired figures return zero occurrences in its exported PDF text.

## 6. What to fix, in order

1. **P1-1** tamper verification — fixed 27 Oct.
2. **P1-2** Data Layer live ID / seed comparison — fixed 27 Oct.
3. **P1-5** one set of matcher numbers across deck, kit and appendix — fixed 27 Oct.
4. **P1-4** team slide to six — fixed 27 Oct.
5. **P1-3** real document digests — fixed 27 Oct.
6. **P2-3** record the video — still open.
7. **P2-2 / P2-1** persistent synthetic ribbon and anonymised names — claims corrected, ribbon still open.
8. ~~**P2-4** relabel the production stack as a plan~~ — done 27 October.
9. **P3-1 / P3-2 / P3-3** polish — fixed 27 Oct.
10. **P2-5** lock the audit append before any real deployment — still open.

## 7. Remediation log — 27 October 2026

All edits were made to the shipped files and re-verified.

| Item | Change | Evidence after the fix |
|---|---|---|
| P1-1 | Removed `rehashAudit()` from every render path. The chain is sealed once by `initAuditChain()` at startup/reset; `addAudit()` only appends; `chainCheck()` recomputes and compares the stored `prev`/`hash` without mutating them. | Seed verifies as “Chain intact · 18 events”. Editing `audit[0].action` and pressing **Verify chain** now reports “Chain broken · row altered or deleted”. A reload after one action keeps 19 entries; a persisted tamper still fails; reset restores head `748b44fc…fc6fe0`. |
| P1-2 | Data Layer heading renders `audit[0].id`; the screen states that the psql comparison is against the seeded 18-row snapshot and tells the presenter to reset before comparing. | QA probe after one action reads “Newest entry · A-1055”; the live hash matches the newest row. |
| P1-3 | Institution documents render a deterministic digest per institution and filename: `sha256(pid + '|' + document)`. | Four documents → four unique 12-character prefixes: `9ed5b3194fdd…`, `887e59d69a87…`, `7c0cca61afea…`, `c153bec2b77b…`. |
| P1-4 | Slide 6 consolidated to Lead 1, Frontend + design 2, Backend 2, Data 1, Total 6; role descriptions and speaker notes match. | Deck reopened clean at revision 8; slide 6 text and notes enumerate six people. |
| P1-5 | One numeric source everywhere: 9,558-ID master, 367 labelled variants, 94.6% top-1, 99.7% top-3, 0 silent merges. Removed 2,726, 95.0, 98.2, 100%, 70.3%, 322, 22% and “labelled on every screen”. | Full-text scans of the HTML, PPTX, preview PDF, kit and appendix return zero occurrences of the retired figures; deck slide 1, deck slide 4, preview pages 1/4, kit pages 1–2, appendix page 1 and the prototype Radar box all agree. |
| P3-1 | Intake banner pluralises case/cases and exists/exist. | QA shows the collision banner with correct grammar at 1 and 3 open cases. |
| P3-2 | Alias chips wrap at narrow widths. | QA at 320/360/390/768/1024/1366/1920 px: 0 horizontal overflow on every width. |
| P3-3 | Added `aria-label` to the bell audit button and the role selector. | QA accessibility probe: 0 unnamed buttons, 0 missing alt, 0 unlabeled inputs. |
| P2-4 | Slide 3 separates prototype from target stack; TF-IDF listed as a matching signal. | Deck revision 11 saved; preview page 3 patched and visually checked. |
| New | Advisory TF-IDF text similarity over complaint narratives plus an extractive two-sentence brief, shown on the Radar and at intake. | Radar surfaces a 0.41 pair at different institutions; intake returns C-2026-0168 at 0.24 with shared terms; both actions are advisory and write to the audit chain only on review/dismissal. |
| New | Official-format idea deck (`Ekasutra_SIH2026_SIH26264_Official.pptx`) built inside the downloaded SIH 2026 template, plus the portal-required PDF exported through PowerPoint COM. | 6 slides, instructions slide deleted, template header/logo/oval/footer preserved; PDF is 6 pages at 960×540 pt; PDF text scan gives 0 occurrences of every retired figure and 3× 9,558, 4× 367, 2× 94.6, 2× 99.7. Team ID on page 1 is left blank in amber for the portal value. |

**Re-run result (`qa/qa_flow.js`):** 9 views navigate with no console errors; intake collision shown; joint room created; tamper detected; live Data Layer ID correct; document digests 4/4 unique; all widths clean; accessibility 0/0/0; **no findings**.

### Still open

- **P2-1 / P2-2 — synthetic-data labelling.** The false “labelled on every screen” claim is gone, and the deck, preview, kit and Data Layer now say the cases are synthetic in plain words. There is still no persistent ribbon on the dashboard or case screens, and public screenshots still pair real institution names with invented complaints. Add the ribbon and anonymise public captures before the video.
- **P2-3 — video.** Not recorded. This is the largest remaining score risk.
- **P2-4 — production stack.** Closed. Slide 3 now labels the stack as the target and states that the prototype is one HTML file.
- **P2-5 — concurrent audit append.** `audit_write()` still reads the chain head without a lock. Serialise with an advisory lock or a `FOR UPDATE` head row before any real deployment.

## 8. Sign-off

The domain model, the demo flow and the visual language are submission-grade. The evidence layer is not yet. Treat this report as the punch list, not a verdict on the idea: the idea is the strongest part of the build.
