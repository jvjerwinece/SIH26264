# QA harness

Playwright checks for the v8 prototype. Read-only: it does not modify `submission/`.

## Run

```bash
npm install
npx playwright install chromium
node qa_flow.js
```

If Playwright's bundled Chromium is not installed, the script tries installed Microsoft Edge and Chrome. Override explicitly:

```bash
QA_CHANNEL=msedge node qa_flow.js
QA_CHANNEL=chrome  node qa_flow.js
```

Screenshots go to `qa/artifacts/` (git-ignored).

## What it checks

1. All nine screens navigate.
2. Console and page errors.
3. Intake → load sample → resolve → joint case.
4. Audit verify before and after an in-memory tamper probe.
5. Data Layer newest-entry label versus the live audit ID.
6. Institution document hash uniqueness.
7. Horizontal overflow at 320–1920 px.
8. Basic accessibility counts (unnamed buttons, missing alts, unlabeled inputs).

## Expected output on v8

The run logs known defects and exits `0` unless there is a console/page error or an unexpected failure. Set `QA_STRICT=1` to exit non-zero on known defects too.

Known findings you should see:

```
TAMPER: hash changed = true | verifier = "Chain intact · 18 events"
DATA LAYER: "Newest entry · A-1054" | live id = A-1055
DOC HASHES: ["4a8e1d3c","9c2f4a7b","9c2f4a7b","9c2f4a7b"]
WIDTH 320 overflow 2
```

- **Tamper not detected** — P1-1. The verifier re-hashes before comparing.
- **Stale label** — P1-2. The header is hardcoded.
- **Repeated hashes** — P1-3. Placeholder values in the institution profile.
- **2 px overflow** — P3-2. Status chip at 320 px.

The exact audit ID after the probe depends on the seed and the actions taken; `A-1055` is typical.

## Notes

- The script uses the same browser profile for the whole run, so `localStorage` carries between steps. That is intentional: it tests persistence. Run the prototype's **Reset demo data** between manual sessions.
- The harness does not test the PostgreSQL layer. Use `database/README.md` for the SQL checks.
- No axe-core run is included; the accessibility counts are a smoke check, not a WCAG audit.
