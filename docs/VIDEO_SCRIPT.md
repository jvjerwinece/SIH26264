# Demo video — 3:00 script (PS 26264)

Shoot from `submission/Ekasutra_v8.html`, the same file in the deck's captures.
Every number below is one of the shipped claims; do not improvise new ones.

## Timeline

| Time | Framework beat | On screen | Action |
|---|---|---|---|
| 0:00–0:18 | Problem & core challenge | Title card, then the dashboard still | None — this is narration over a slow push-in |
| 0:18–0:45 | Why it is a game-changer | Dashboard, thread card top-right | Hover the three-case thread |
| 0:45–1:15 | Core innovation / differentiator | Case Intake → results, then Audit Log | Type the messy name, resolve, confirm |
| 1:15–2:40 | Prototype walkthrough | Dashboard → Case Intake → Radar → Room → Audit → Reports | Click through in this order |
| 2:40–3:00 | Long-term impact & vision | Bench numbers on the Radar sidebar, then the deck's page 5 still | None |

## Voice-over

**[0:00] Problem.**
One college. Three complaints. Three offices. A grievance about a single institution can reach the RB, the PGRC, or a regional office, and each office types the name its own way. Nobody is wrong — but the register ends up holding three records of one institution, and no officer can see the other two.

**[0:18] Why it is different.**
Ekasutra fixes one thing: the complaint is resolved to the institution once, by its AICTE Permanent ID. From that moment every bureau works the same thread — one owner at a time, one history, and one place to look before you act. It is not another complaints portal. It is the coordination layer across the ones AICTE already runs.

**[0:45] Core innovation.**
Matching is rules-first, and it shows its reasons. Exact ID, alias, spelling distance, city — each signal is listed, and a person confirms. A score never merges two cases on its own. Every decision is written to a hash-chained audit trail, so the register can prove who linked what, and when.

**[1:15] Walkthrough.**
This is the prototype. One HTML file. No server, no login, and it runs offline.

Thirty-two seeded cases. Top right, one thread: three cases about the same college — two with PGRC, one with the RB — already on a single timeline.

Now intake. I paste a complaint where the college name is abbreviated and misspelled. Resolve. The matcher returns the closest institutions, and beside each one, why: the ID matches, the alias matches, the city matches. I confirm the right institution — and only then do the cases link.

The overlap radar does the same work across the whole register. Here is a ninety-eight percent cluster: all three cases side by side, and the evidence in plain language.

Opening the coordination room turns a message into a decision. Both bureaus see the same room, the same decision, and the same timestamp.

Every one of those actions lands here. Eighteen events, each hashed into the one before it. If a row is edited, the verifier reports the chain as broken.

And the whole register filters and exports to CSV for the report the bureau already files.

**[2:40] Impact.**
On our own labelled set, three hundred and sixty-seven name variants resolve at ninety-four point six percent top-one, and ninety-nine point seven percent in the top three — with zero silent merges. The next step is a six-week pilot in one region: connect the master, keep the current intake channels, and switch the audit lock on before it handles a single real complaint.

## Shot list

1. **Dashboard** (12s) — no clicks. Let the thread card sit in frame.
2. **Case Intake** (20s) — paste `V.S. College of Engg., Kanchipuram` with a short narrative, click **Resolve & check**, pause 2s on the candidates, click the top one, confirm.
3. **Radar** (18s) — scroll until the 98% card is centred, hover the evidence chips.
4. **Coordination Room** (12s) — click **Open Coordination Room**, stop on the decision panel.
5. **Audit Log** (12s) — stop on "Chain intact · 18 events". Click **Verify chain**.
6. **Reports** (11s) — set one filter, show the KPI band change, click **Export CSV**.

## Recording settings

- Browser window 1440×810, full screen, zoom 100%. Recording that region and delivering 1920×1080 uplifts the interface by 1.33× — the 13 px body reads as 17 px, the 9.5 px labels as 12.7 px.
- Hide the bookmarks bar. Close every other tab. Turn off notifications.
- Leave the amber "SYNTHETIC DEMO DATA" ribbon in frame — it is the honest label.
- Move the cursor slowly and click only what the script names. No scrolling during narration except beats 1 and 3.
- Record room tone separately; the demo has no sound.

## Do not say

- "real AICTE data" or "live government data" — the seed is synthetic.
- "100% accurate", "automatically merges", "AI decides" — matching is rules-first and a person confirms.
- "production ready", "replaces CPGRAMS" — the pilot, the roles and the audit lock are future work.
- Any number that is not in the deck: 9,558 IDs, 367 variants, 94.6% top-1, 99.7% top-3, 0 silent merges, 18 audit events, 32 cases, 11 tables, 98% cluster.
- The 100–200 officer-days figure without "modelled".

## Cutaway cards (optional, 2–4 s each)

Five stills that can sit between live actions. Every prompt ends with the style block; none of them may contain text — the generator garbles it, and a garbled label is worse than no image.

**Style block, append to every prompt:**
```
flat editorial infographic, matte bone-paper background #F4F1EA, line art in ink navy
#1F2A44 at 2-3px, one accent per image (muted brick #B3542F or steel blue #2B5C8A),
flat fills, no gradients, no drop shadows, no glow, no 3D, no isometric, generous
margins, calm symmetric composition, single focal point, 16:9, absolutely no text,
no letters, no numbers, no logos, no watermarks
```

1. **The problem (0:00).** One small line-art building at centre; three identical folder icons around it at equal distance, each joined to the building by a different-coloured path that never touches the other two. The negative space between the paths is the point.
2. **Resolve once, then one thread (0:18).** Three scattered paper-sheet icons entering from the left, converging into a single small ID-badge icon at centre; from the badge one clean horizontal line runs into a stacked timeline of three connected nodes. Left side unaligned, right side calm, same line weight throughout.
3. **Reasons, not a score (0:45).** A single decision node with three thin labelled-by-shape branches: a solid checkmark branch, a dotted uncertain branch, and a hard stop. No arrows in a circle, no funnel cliché.
4. **The audit chain (1:15).** Five or six short horizontal bars in a row, each overlapping the previous by a third, joined by a hairline that runs through their centres; one bar is a different colour to suggest an edited row and the hairline visibly breaks at it.
5. **Reach (2:40).** A sparse grid of about forty small dot markers with one connected cluster ringed in accent colour, and a thin bracket linking that cluster to a plain rectangular register block at the right edge. No globe, no map outlines.

Place them only where the framework asks for a beat, and cut any that are not ready: the walkthrough is 85 s of the 180 s and it should not be diluted.

