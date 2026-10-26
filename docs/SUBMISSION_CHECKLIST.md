# Submission checklist

**Deadline:** 28 October 2026
**Build:** v8, cut 25 October 2026
**Status as of 27 October 2026:** P1 defects fixed and re-verified; **video missing**.

---

## 1. Artifact status

| Artifact | File | Status | Gate |
|---|---|---|---|
| Prototype | `submission/Ekasutra_v8.html` | Ready; P1-1/2/3 fixed and re-tested | Tamper test is safe to demo |
| Deck | `submission/Ekasutra_SIH2026_SIH26264.pptx` | Ready; team and metrics fixed; P2-4 open | Relabel the production stack when time allows |
| Deck preview | `submission/Ekasutra_SIH2026_SIH26264_preview.pdf` | Regenerated to match the edited deck | Spot-check pages 1, 4 and 6 |
| Data appendix | `submission/Ekasutra_Data_Appendix.pdf` | Ready; unsupported reconciliation line removed | Keep as the numeric source |
| Submission kit | `submission/Ekasutra_Submission_Kit.pdf` | Claims corrected; duration note open | Rehearse to 2:50 |
| Database pack | `submission/Ekasutra_Database_Pack.zip` | Ready | Do not modify after checksum |
| Video | — | **Not recorded** | Record 2:50 |
| Repository | this repo | Ready locally | Push after review |

## 2. Fixes and remaining work

P1 items are done and verified. Remaining work, in order. Full detail in `QA_REPORT.md`.

- [x] **P1-1** Make the browser audit check verify stored hashes without re-sealing edits.
- [x] **P1-2** Render the live newest audit ID; make the psql comparison explicit about the seeded snapshot.
- [x] **P1-3** Replace the three placeholder document hashes with real seeded digests.
- [x] **P1-4** Reduce the team slide to six people including the lead; update notes.
- [x] **P1-5** Use one numeric source: 367 variants, 94.6% top-1, 99.7% top-3, 9,558-ID master. Removed 2,726 / 95.0 / 98.2 / 100% / 70.3% / 322 from every artifact.
- [ ] **P2-3** Record the video and verify duration.
- [x] **P2-2** Correct the “labelled on every screen” answer; the persistent ribbon is still open (P2-1).
- [ ] **P2-1** Add the ribbon; anonymise institution names in public screenshots.
- [ ] **P2-4** Relabel slide 3 as prototype vs target stack.
- [x] Regenerate the deck preview PDF after the slide edits.
- [x] Regenerate `submission/SHA256SUMS.txt` after the file changes.
- [x] Re-run `qa/qa_flow.js`; no findings, no console errors, 0 overflow, A11Y 0/0/0.

## 3. Video specification

| Item | Requirement |
|---|---|
| Duration | **2:50 target**, 3:00 hard limit; check the portal limit before recording |
| Resolution | 1920×1080, 16:9 |
| Format | MP4, H.264, AAC audio |
| Audio | Clear voice, no clipping, no copyrighted music |
| Capture | Browser at 100% zoom, 1366×900 or 1920×1080; hide bookmarks and notifications |
| Data | Synthetic; show the label; do not show real complaint allegations |
| Claims | Use only the appendix numbers |
| Ending | One sentence, one ask; no dead air |
| Verification | Play on a phone, check duration, check audio, check the first and last 3 seconds |

### Shot list (2:50)

| Time | Screen | Action | Line |
|---|---|---|---|
| 0:00–0:15 | Dashboard | Hold on the overlap/ownership summary | The same institution reaches AICTE through two windows, and nobody owns the whole picture. |
| 0:15–0:35 | Dashboard | Point to one institution, one thread, one owner | Ekasutra makes the institution the unit, not the case. |
| 0:35–1:00 | Case Intake | Load sample → Resolve & check | Permanent ID first, alias graph second, trigram third. The match is explainable. |
| 1:00–1:25 | Case Intake | Show open cases → Create joint case | The system refuses to create a silent duplicate. Link, joint, or proceed with a written reason. |
| 1:25–1:50 | Coordination Room CR-01 | Set lead bureau, joint decision | One room, one lead, one decision; both bureaus keep their own records. |
| 1:50–2:10 | Room | Escalate or merge duplicate; show activity | Escalation needs a reason; a merge keeps the absorbed case linked. |
| 2:10–2:30 | Audit Log | Verify chain; open Data Layer | Every action commits to the previous hash; the same formula runs in PostgreSQL. |
| 2:30–2:45 | Reports / Institution profile | One institution thread | This is the view neither bureau has today. |
| 2:45–2:50 | Deck slide 1 or dashboard | Close | One institution, one thread, one owner, one proof. |

The tamper test is now safe to demo: edit a row, press **Verify chain**, and reset afterwards. The Data Layer reports the live entry and labels the psql comparison as the seeded snapshot; reset before comparing.

## 4. Pre-upload verification

```bash
cd submission
sha256sum -c SHA256SUMS.txt
```

Then:

- [ ] Open `Ekasutra_v8.html` from a clean profile with network disabled.
- [ ] Run the 90-second tour end to end.
- [ ] Reset demo data; confirm 18 audit events.
- [ ] Open the deck on a different machine; confirm fonts and 16:9.
- [ ] Open the kit and appendix; confirm 2 pages each and no clipped text.
- [ ] Unzip the database pack into a temp folder; confirm six files and the appendix path.
- [ ] Confirm the video plays on a phone with sound.
- [ ] Confirm the upload form accepts each file type and size.
- [ ] Keep an untouched copy of the six files plus the video outside the repo.

## 5. Upload steps

1. Verify checksums.
2. Upload the six files in `submission/` — not the repository, not the archive folders.
3. Upload the video or paste its link, following the portal's naming rule.
4. Download each uploaded file back and open it once.
5. Record the submission ID, timestamp and a screenshot of the confirmation.
6. Tag the repo: `git tag v8-submission && git push --tags`.

## 6. If time runs short

Priority order:

1. Video — without it, the submission is incomplete.
2. P2-4 — relabel slide 3 as prototype vs target stack; a false equivalence is easy for a judge to catch.
3. P2-1 — add the synthetic ribbon and anonymise public screenshots.
4. P2-5 — lock the PostgreSQL audit append before any deployment beyond the demo.

Do not regenerate the deck at the last minute without re-checking every page. A stale preview PDF is worse than a known-good older deck.
