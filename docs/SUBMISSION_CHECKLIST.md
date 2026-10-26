# Submission checklist

**Deadline:** 28 October 2026
**Build:** v8, cut 25 October 2026
**Status as of 26 October 2026:** documents ready, **video missing**, five P1 defects open.

---

## 1. Artifact status

| Artifact | File | Status | Gate |
|---|---|---|---|
| Prototype | `submission/Ekasutra_v8.html` | Ready, defects P1-1/2/3 open | Fix or avoid live tamper test |
| Deck | `submission/Ekasutra_SIH2026_SIH26264.pptx` | Ready, P1-4/P1-5/P2-4 open | Fix numbers and team slide |
| Deck preview | `submission/Ekasutra_SIH2026_SIH26264_preview.pdf` | Matches deck | Regenerate after deck edits |
| Data appendix | `submission/Ekasutra_Data_Appendix.pdf` | Ready, consistent with DB | Keep as the numeric source |
| Submission kit | `submission/Ekasutra_Submission_Kit.pdf` | Ready, P1-5/P2-2/P2-3 open | Fix claims and duration |
| Database pack | `submission/Ekasutra_Database_Pack.zip` | Ready | Do not modify after checksum |
| Video | — | **Not recorded** | Record 2:50 |
| Repository | this repo | Ready locally | Push after review |

## 2. Blocking fixes before upload

Do these in order. Full detail in `QA_REPORT.md`.

- [ ] **P1-1** Make the browser audit check verify stored hashes without re-sealing edits.
- [ ] **P1-2** Render the live newest audit ID; make the psql comparison explicit about the seeded snapshot.
- [ ] **P1-3** Replace the three placeholder document hashes with real seeded digests.
- [ ] **P1-4** Reduce the team slide to six people including the lead; update notes.
- [ ] **P1-5** Use one numeric source: 367 variants, 94.6% top-1, 99.7% top-3, 9,558-ID master. Remove 2,726 / 95.0 / 98.2 / 100% / 70.3% / 322 unless the harness is shipped.
- [ ] **P2-3** Record the video and verify duration.
- [ ] **P2-2** Add a persistent synthetic-data label or correct kit Q4.
- [ ] **P2-1** Label illustrative IDs; anonymise institution names in public screenshots.
- [ ] **P2-4** Relabel slide 3 as prototype vs target stack.
- [ ] Regenerate the deck preview PDF after any slide edit.
- [ ] Regenerate `submission/SHA256SUMS.txt` after any file change.
- [ ] Re-run `qa/qa_flow.js`; confirm no regressions.

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

Do not demo the tamper test until P1-1 is fixed. Do not show the Data Layer after performing actions; either reset first or fix P1-2.

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
2. Numeric consistency — the fastest credibility win.
3. Team slide — an eligibility contradiction.
4. Tamper verification — the highest-value technical fix, but only if there is time to re-test.
5. Document hashes and Data Layer label — polish for a live demo.

Do not regenerate the deck at the last minute without re-checking every page. A stale preview PDF is worse than a known-good older deck.
