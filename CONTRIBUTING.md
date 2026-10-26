# Contributing

This repository is the v8 submission snapshot plus the material needed to review, reproduce and extend it. Treat `submission/` as frozen evidence, not as a working directory.

---

## 1. Ground rules

1. **No real complaint data.** No complainant names, case correspondence, officer personal data or unredacted documents. The demo seed is synthetic. See `docs/DATA_NOTICE.md`.
2. **No secrets.** No tokens, database URLs, API keys or credentials in any file, commit or issue.
3. **Do not rewrite submission files in place.** If you change the prototype or deck, create the new build, verify it, then replace the file and regenerate `submission/SHA256SUMS.txt` in the same commit.
4. **Keep the seed deterministic.** `generate_demo_seed.py` must produce byte-identical SQL for the same JSON.
5. **One source of truth for claims.** Numbers live in `docs/DATA_NOTICE.md` and the appendix. Do not introduce a new headline metric without a reproducible harness.

## 2. Setup

### Prototype

```bash
# no build step
start submission/Ekasutra_v8.html        # Windows
open submission/Ekasutra_v8.html         # macOS
```

Use Chrome or Edge. Test with the network disabled at least once.

### Database

PostgreSQL 14+:

```bash
createdb ekasutra_demo
psql -d ekasutra_demo -f database/schema.sql
psql -d ekasutra_demo -f database/seed_demo.sql
psql -d ekasutra_demo -c "select * from audit_verify();"
```

Expected: 18 audit rows, `ok = true`, head `748b44fc1aad8e9a1c05d0040b54e95f68d966ea5396dffc789139aab9fc6fe0`.

### QA harness

```bash
cd qa
npm install
npx playwright install chromium
node qa_flow.js
```

Set `QA_CHANNEL=chrome` or `QA_CHANNEL=msedge` to use an installed browser. Set `QA_STRICT=1` to fail on known defects as well as unexpected errors. See `qa/README.md`.

## 3. Branching and commits

- Branch from `main`: `feat/custody-state-machine`, `fix/audit-verify`, `docs/video-script`.
- Commit style: imperative subject, one logical change.
  - `fix: verify stored audit hashes without re-sealing`
  - `docs: replace unsupported matcher claims with appendix figures`
  - `feat: add explicit custody transitions`
- Do not commit generated artifacts (`qa/artifacts/`, `node_modules/`).
- Do not tag a release until checksums, deck preview and QA are consistent.

## 4. Changing the prototype

The prototype is a single HTML file. There is no bundler, so keep it that way unless the team deliberately starts the production app.

Checklist for any prototype change:

- [ ] No new console or page errors on load.
- [ ] All nine screens navigate.
- [ ] Intake → resolve → joint case → room → audit still works.
- [ ] Reset restores 18 audit events.
- [ ] 320, 390, 768, 1366 and 1920 px show no new overflow.
- [ ] Any new user-facing string is plain English and does not claim a capability that is not built.
- [ ] If the seed changed, update `demo_seed.json`, regenerate `seed_demo.sql`, and mirror the rows in the HTML.

### Audit changes

The audit formula is a contract:

```
sha256(prev_hash || UTC time || actor || action || object)
```

If you touch `chainHash`, `auditTime`, `audit_write` or `audit_verify`, update the appendix and re-verify both sides. Never call a rehash function from a render path — that is how P1-1 happened.

## 5. Changing the deck or documents

The deck is a binary `.pptx`; there is no generator in this repository.

- Edit in PowerPoint, keep 16:9.
- Re-export `Ekasutra_SIH2026_SIH26264_preview.pdf`.
- If a screenshot changes, re-capture it from the current HTML and replace the image in the deck; do not mix builds.
- Re-check slide 6 team size (six including the lead).
- Re-check that every number matches `docs/DATA_NOTICE.md`.
- Update the appendix if the architecture or metrics changed.

## 6. Checksums and submission files

After any change under `submission/`:

```bash
cd submission
sha256sum Ekasutra_v8.html \
         Ekasutra_SIH2026_SIH26264.pptx \
         Ekasutra_SIH2026_SIH26264_preview.pdf \
         Ekasutra_Data_Appendix.pdf \
         Ekasutra_Submission_Kit.pdf \
         Ekasutra_Database_Pack.zip > SHA256SUMS.txt
sha256sum -c SHA256SUMS.txt
```

Commit the changed file and the checksum file together.

## 7. Pull request checklist

- [ ] Scope is one change; description says why.
- [ ] No real data, no secrets, no credentials.
- [ ] `docs/DATA_NOTICE.md` claim register updated if any claim changed.
- [ ] `qa/qa_flow.js` run; output attached or summarized.
- [ ] Checksums regenerated if `submission/` changed.
- [ ] Deck preview regenerated if the deck changed.
- [ ] No old builds, renders or archives added.

## 8. What not to add

The v1–v7 builds, earlier deck renders, stale screenshots and the full archive are intentionally excluded. They live outside this repository. If provenance is needed, link to the archive rather than copying it in.
