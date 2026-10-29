# Deployment — Vercel → Render → Supabase

The demo stack takes about 20 minutes to stand up on free tiers. No card is required, and the browser never receives a database credential.

```
custom domain / *.vercel.app
        │  same origin
        ▼
Vercel  web/ static dashboard + api/[...path].js proxy
        │  HTTPS, server-to-server
        ▼
Render  Docker image from server/, FastAPI + psycopg pool
        │  DATABASE_URL, sslmode=require
        ▼
Supabase  PostgreSQL, schema + seed from database/Ekasutra_Supabase.sql
```

What the deployment is **not**: a production pilot. There is no login, the `X-Demo-Role` header is a demo switch, uploads are metadata only, and all complaint data is synthetic. `/api/meta` reports those limits.

---

## 0. Prerequisites

- This repository pushed to GitHub (the Render and Vercel projects build from it).
- Free accounts on [Supabase](https://supabase.com), [Render](https://render.com), [Vercel](https://vercel.com).
- The custom domain, with access to its DNS records.

Files that do the work:

| File | Purpose |
|---|---|
| [`database/Ekasutra_Supabase.sql`](../database/Ekasutra_Supabase.sql) | schema + seed for a fresh Supabase project |
| [`database/Ekasutra_Supabase_Reset.sql`](../database/Ekasutra_Supabase_Reset.sql) | truncate + reseed an existing demo project |
| [`render.yaml`](../render.yaml) | Render Blueprint (Docker, `server/`, `/health`) |
| [`server/Dockerfile`](../server/Dockerfile) | API image |
| [`web/vercel.json`](../web/vercel.json) | static project config, `sin1` function region, security headers |
| [`web/api/[...path].js`](../web/api/[...path].js) | same-origin proxy to Render |

---

## 1. Supabase — database

1. **New project.** Region: Mumbai (`ap-south-1`) if offered, otherwise the nearest Asia region. Save the database password.
2. **SQL Editor → New query.** Paste the entire contents of `database/Ekasutra_Supabase.sql` and run it. It creates `pg_trgm`, eleven tables, the view, the matcher and the audit functions, then loads the seed.
3. **Read the final result row.** It must be:

   ```
   cases | audit_rows | chain_ok | chain_head
   32    | 18         | t        | 748b44fc1aad8e9a1c05d0040b54e95f68d966ea5396dffc789139aab9fc6fe0
   ```

   If `chain_ok` is not `t`, stop; do not point the API at it.
4. **Connection string.** Project Settings → Database → **Connection string → Session pooler** (port `5432`, host `...pooler.supabase.com`). Replace the password placeholder and keep `?sslmode=require`. It looks like:

   ```
   postgresql://postgres.<project-ref>:<password>@aws-0-ap-south-1.pooler.supabase.com:5432/postgres?sslmode=require
   ```

   Use the **session pooler**, not the direct connection: it is IPv4-reachable and survives Render's network. The API sets `prepare_threshold=None` so psycopg does not use named prepared statements through Supavisor.

**Reset the demo later:** run `database/Ekasutra_Supabase_Reset.sql` in the SQL editor. It deletes every row the demo created and reloads the seed; the chain head returns to `748b44fc…fc6fe0`. Never run it against the national master.

---

## 2. Render — API

1. **New → Blueprint.** Select the repository. Render reads [`render.yaml`](../render.yaml): Docker service `ekasutra-api`, root directory `server`, free plan, Singapore, health check `/health`.
2. **Set the secret.** When prompted for `DATABASE_URL`, paste the Supabase session-pooler string from step 1. `ALLOWED_ORIGINS` can stay empty because the Vercel proxy is server-to-server.
3. **Deploy.** First build takes a few minutes.
4. **Verify** `https://<service>.onrender.com/health`:

   ```json
   {"ok":true,"database":"up","entries":18,"chain_ok":true}
   ```

5. **Verify the contract** at `/api/meta`: `stats.cases` is 32, `stats.audit_entries` is 18, `chain.ok` is true, and `demo.auth` is false.

If you prefer a manual service instead of the Blueprint: New → Web Service → Docker → root directory `server`, Dockerfile `Dockerfile`, health check `/health`, env `DATABASE_URL`, `DB_POOL_MAX=5`.

**Free-tier behaviour:** the service sleeps after 15 minutes of inactivity and takes roughly 30–60 seconds to wake. The dashboard renders its offline seed immediately and switches to live when `/api/bootstrap` answers, so a cold start shows content rather than a spinner.

---

## 3. Vercel — frontend

1. **Add New → Project**, import the same repository.
2. **Root Directory:** `web`. Framework preset: **Other**. Build command: leave empty. Output directory: leave empty (Vercel serves the directory and detects `api/`).
3. **Environment variable:** `EKASUTRA_API_ORIGIN` = the Render URL from step 2, no trailing slash and no `/api`, e.g. `https://ekasutra-api.onrender.com`.
4. **Deploy.** Open the `*.vercel.app` URL. The sidebar footer should read **● Live · Supabase + Render**; the Data Layer should show 32 cases and 18 audit rows with **CONNECTED**.

If the footer says **Offline file · no API**, the browser is on `file://` or `/api/bootstrap` failed. Check the proxy:

```
https://<project>.vercel.app/api/meta
```

A `503` means `EKASUTRA_API_ORIGIN` is missing. A `502` means the proxy could not reach Render within 55 s or the API errored; open `/health` on Render directly. A sleeping free-tier service is retried by the dashboard, so a cold start alone should not produce a permanent fallback.

---

## 4. Custom domain

Do this on Vercel only; Render stays behind the proxy.

1. Vercel project → **Settings → Domains → Add**. Enter the apex domain, e.g. `ekasutra.example`.
2. At the DNS provider add the records Vercel shows. For most providers:

   | Type | Name | Value |
   |---|---|---|
   | A | `@` | `76.76.21.21` |
   | CNAME | `www` | `cname.vercel-dns.com` |

   If the provider supports `ALIAS`/`ANAME` at the apex, use the value Vercel displays instead of the A record.
3. Wait for **Valid Configuration** and the automatic TLS certificate.
4. Add the domain to Render's `ALLOWED_ORIGINS` **only** if you switch to direct API calls (below). With the proxy, leave it empty.

No code change is needed: `config.js` keeps `window.EKASUTRA_API = ""`, so every request goes to `/api/*` on the domain the page was loaded from.

### Optional: call Render directly

If you want to skip the Vercel function, set `web/config.js` to the Render URL and set `ALLOWED_ORIGINS` on Render to the comma-separated site origins:

```js
window.EKASUTRA_API = "https://ekasutra-api.onrender.com";
```

```env
ALLOWED_ORIGINS=https://ekasutra.example,https://ekasutra.vercel.app
```

The proxy is the default because it keeps one origin, avoids CORS drift and hides the API host.

---

## 5. Local end-to-end check

The stack was verified on 29 October 2026 with PostgreSQL 16.15, Python 3.12 and a Chromium browser.

```bash
# 1. database (any local PostgreSQL 14+)
createdb ekasutra_demo
psql -d ekasutra_demo -f database/schema.sql
psql -d ekasutra_demo -f database/seed_demo.sql   # sets client_encoding to utf8 itself

# 2. API (serves web/ too when it exists)
cd server
python -m venv .venv && . .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export DATABASE_URL='postgresql://postgres@127.0.0.1:5432/ekasutra_demo?sslmode=disable'
uvicorn app:app --port 8000

# 3. open http://127.0.0.1:8000/
```

Evidence from that run:

| Check | Result |
|---|---|
| `/health` | `{"ok":true,"database":"up","entries":18,"chain_ok":true}` |
| Dashboard footer | `● Live · Supabase + Render`, 32 cases loaded from the API |
| Intake → sample → resolve → Proceed with reason | Case `C-2026-0199` committed; toast names PostgreSQL; audit 18 → 19 |
| Case dispose → reopen | Events written with actor `R. Menon`, then `P. Rao` after the role switch; chain 19 → 21 |
| Data Layer counts | `cases 33`, `case_events 130`, `audit_entries 19` — equal to SQL counts, not estimates |
| Verify chain in PostgreSQL | `SHA-256 chain verified in PostgreSQL · 19 entries` |
| Vercel proxy handler (local harness) | bootstrap 200, audit verify 200, matcher 200, invalid POST 422, `..` path blocked 400 |
| Clean reset | truncate + seed returns 32 cases, 18 rows, head `748b44fc…fc6fe0` |
| Audit append under 20 parallel writers | 18 → 38 rows, 38 distinct `prev_hash`, 0 duplicates, `audit_verify()` ok |
| Fresh bundle into an empty database | 32 cases, 18 rows, `chain_ok = true` |

Not verified here: the Docker image (no Docker on the dev machine, first build is on Render), Supavisor transaction pooling, Render cold starts, and TLS to Supabase. Those four only resolve once the projects exist.

### Cold starts

Render's free plan sleeps after 15 minutes. The first request can take 30–50 s. The proxy allows 55 s and its Vercel function is configured for `maxDuration: 60`; the dashboard renders the seed immediately, shows `Live stack waking · retry n/6` in the footer and keeps retrying for about 45 s before falling back to the offline pack. Open the URL once before a demo and leave the tab warm.

---

## 6. Cost and limits

| Service | Free tier used | Limit that matters |
|---|---|---|
| Supabase | 500 MB database | Project pauses after ~1 week idle; resumes on request |
| Render | 512 MB Docker web service | Sleeps after 15 min idle; 750 instance-hours/month |
| Vercel | Hobby | 100 GB bandwidth/month; one serverless function here |

All three are demo hosts. Do not present their limits as a capacity claim for a national rollout.
