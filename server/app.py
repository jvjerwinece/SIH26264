"""Ekasutra demo API — FastAPI over the PostgreSQL pack in database/.

The browser never holds a database credential. Every write is one transaction
that updates the ledger, appends a case event, and calls audit_write(); the
actor is resolved from a seeded user, never from the request body.

This is a demo deployment, not the production pilot: there is no login, the
role header is a demo switch, and uploads are metadata only. /api/meta says so
so no screen has to imply otherwise.
"""
from __future__ import annotations

import os
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import db

ROOT = Path(__file__).resolve().parent
WEB = ROOT.parent / "web"

ROLE_USERS = {
    "RB Officer": "R. Menon",
    "PGRC Officer": "P. Rao",
    "Senior Management": "Director, AICTE",
    "Regional Office": "S. Iyer",
}
BUREAU = {"RB": "RB", "PGRC": "PGRC", "Regional Office": "RO", "RO": "RO"}
BUREAU_UI = {"RB": "RB", "PGRC": "PGRC", "RO": "Regional Office"}
SLA = {
    "Harassment complaint": 45,
    "Unauthorized intake": 90,
    "Unapproved intake": 90,
    "Approval violation": 90,
    "Unapproved course": 90,
}
MAX_BODY = 500


# --------------------------------------------------------------------- queries
INSTITUTIONS = """
select i.id,
       i.permanent_id as pid,
       i.name,
       i.city,
       i.state,
       i.region,
       i.address,
       coalesce(nullif(i.trust_name, ''), '—') as trust,
       coalesce((select json_agg(a.alias order by a.alias)
                 from institution_aliases a
                 where a.institution_id = i.id), '[]'::json) as aliases
from institutions i
order by i.id
"""

CASES = """
select c.case_no as id,
       'i' || c.institution_id as inst_id,
       c.category,
       c.bureau,
       c.status,
       to_char(c.received_on, 'YYYY-MM-DD') as received,
       coalesce(c.last_action, '') as last_action,
       coalesce(c.next_action, '') as next_action,
       to_char(c.last_action_on, 'YYYY-MM-DD') as last_action_date,
       to_char(c.expected_disposal, 'YYYY-MM-DD') as expected,
       coalesce(u.full_name, 'Unassigned') as officer,
       c.sla_days,
       (select count(*) from documents d where d.case_id = c.id)::int as docs,
       coalesce(c.summary, '') as summary
from cases c
left join users u on u.id = c.officer_id
"""

CASE_ONE = CASES + " where c.case_no = %s"

OVERLAPS = """
select o.ref as id,
       'i' || o.institution_id as inst_id,
       coalesce((select json_agg(c.case_no order by c.case_no)
                 from overlap_cases oc
                 join cases c on c.id = oc.case_id
                 where oc.overlap_id = o.id), '[]'::json) as case_ids,
       o.confidence::float8 as confidence,
       coalesce(o.reason, '[]'::jsonb) as reason,
       o.state,
       r.ref as room,
       coalesce(r.lead_bureau, 'Unassigned') as lead,
       to_char(o.detected_at at time zone 'Asia/Kolkata', 'DD Mon YYYY, HH24:MI') as detected
from overlap_clusters o
left join rooms r on r.overlap_id = o.id
order by o.id
"""

ROOMS = """
select r.ref as id,
       o.ref as overlap_id,
       coalesce(r.lead_bureau, 'Unassigned') as lead,
       coalesce(r.custody, '') as custody,
       (r.escalated_at is not null) as escalated,
       coalesce((select json_agg(json_build_object(
                    't', to_char(ra.at at time zone 'Asia/Kolkata', 'DD Mon HH24:MI'),
                    'a', ra.actor,
                    'x', ra.action) order by ra.at)
                 from room_activity ra
                 where ra.room_id = r.id), '[]'::json) as activity
from rooms r
join overlap_clusters o on o.id = r.overlap_id
order by r.id
"""

AUDIT = """
select 'A-' || id as id,
       to_char(at at time zone 'Asia/Kolkata', 'YYYY-MM-DD HH24:MI') as time,
       actor,
       action,
       object as obj,
       hash,
       prev_hash as prev
from audit_entries
order by id desc
limit %s
"""

STATS = """
select (select count(*) from institutions)::int      as institutions,
       (select count(*) from institution_aliases)::int as aliases,
       (select count(*) from users)::int             as users,
       (select count(*) from cases)::int             as cases,
       (select count(*) from case_events)::int       as case_events,
       (select count(*) from documents)::int         as documents,
       (select count(*) from overlap_clusters)::int  as overlaps,
       (select count(*) from rooms)::int             as rooms,
       (select count(*) from audit_entries)::int     as audit_entries
"""


# ------------------------------------------------------------------ app setup
@asynccontextmanager
async def lifespan(_: FastAPI):
    db.start()
    yield
    db.stop()


app = FastAPI(title="Ekasutra · SIH26264", version="1.0.0", lifespan=lifespan)

origins = [o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "").split(",") if o.strip()]
if origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["content-type", "x-demo-role"],
        max_age=600,
    )

_hits: dict[str, deque] = defaultdict(deque)


@app.middleware("http")
async def write_limit(request: Request, call_next):
    if request.method == "POST":
        forwarded = request.headers.get("x-forwarded-for", "")
        ip = forwarded.split(",")[0].strip() or (request.client.host if request.client else "unknown")
        now = time.monotonic()
        bucket = _hits[ip]
        while bucket and now - bucket[0] > 60:
            bucket.popleft()
        if len(bucket) >= 120:
            return JSONResponse({"detail": "Too many writes. Try again in a minute."}, status_code=429)
        bucket.append(now)
    return await call_next(request)


# -------------------------------------------------------------------- helpers
def actor(role: str | None) -> dict:
    name = ROLE_USERS.get(role or "RB Officer", ROLE_USERS["RB Officer"])
    row = db.one("select id, full_name, role, bureau from users where full_name = %s", (name,))
    if not row:
        raise HTTPException(503, "Demo users are missing. Load database/seed_demo.sql first.")
    return row


def audit(conn, who: str, action: str, obj: str) -> str:
    return conn.execute("select audit_write(%s, %s, %s) as hash", (who, action, obj)).fetchone()["hash"]


def case_row(conn, case_no: str) -> dict:
    row = conn.execute(CASE_ONE, (case_no,)).fetchone()
    if not row:
        raise HTTPException(404, f"Case {case_no} not found")
    return {
        "id": row["id"],
        "instId": row["inst_id"],
        "category": row["category"],
        "bureau": BUREAU_UI.get(row["bureau"], row["bureau"]),
        "status": row["status"],
        "received": row["received"],
        "lastAction": row["last_action"],
        "nextAction": row["next_action"],
        "lastActionDate": row["last_action_date"],
        "expected": row["expected"],
        "officer": row["officer"],
        "sla": row["sla_days"],
        "docs": row["docs"],
        "summary": row["summary"],
    }


def resolve_institution(conn, value: str) -> dict:
    value = (value or "").strip()
    if value.startswith("i") and value[1:].isdigit():
        row = conn.execute("select id, permanent_id, name, state from institutions where id = %s", (int(value[1:]),)).fetchone()
    elif "-" in value:
        row = conn.execute("select id, permanent_id, name, state from institutions where permanent_id = %s", (value,)).fetchone()
    else:
        row = conn.execute("select id, permanent_id, name, state from institutions where lower(name) = lower(%s)", (value,)).fetchone()
    if not row:
        raise HTTPException(404, f"Institution {value!r} is not in the master")
    return row


def text_field(value: str | None, field: str, minimum: int, maximum: int = MAX_BODY) -> str:
    clean = " ".join((value or "").split())
    if len(clean) < minimum:
        raise HTTPException(422, f"{field} is required")
    return clean[:maximum]


# --------------------------------------------------------------------- models
class NewCase(BaseModel):
    institution: str
    category: str
    summary: str
    bureau: str = "RB"
    complaint: str = ""
    duplicateReason: str | None = None


class CaseAction(BaseModel):
    type: str
    officer: str | None = None
    to: str | None = None
    outcome: str | None = None
    reason: str | None = None
    text: str | None = None


class RoomAction(BaseModel):
    type: str
    lead: str | None = None
    text: str | None = None
    reason: str | None = None


class Dismiss(BaseModel):
    reason: str | None = None


# --------------------------------------------------------------------- routes
@app.get("/health")
def health():
    if not db.configured():
        return JSONResponse({"ok": False, "database": "not configured"}, status_code=503)
    try:
        row = db.one("select 1 as ok, (select count(*) from audit_entries) as entries")
        chain = db.one("select * from audit_verify()")
    except Exception as exc:  # connection refused, pool timeout, wrong schema
        return JSONResponse({"ok": False, "database": str(exc).splitlines()[0]}, status_code=503)
    return {"ok": True, "database": "up", "entries": row["entries"], "chain_ok": chain["ok"]}


@app.get("/api/bootstrap")
def bootstrap():
    with db.connection() as conn:
        institutions = conn.execute(INSTITUTIONS).fetchall()
        cases = conn.execute(CASES + " order by c.case_no").fetchall()
        overlaps = conn.execute(OVERLAPS).fetchall()
        rooms = conn.execute(ROOMS).fetchall()
        audit_rows = conn.execute(AUDIT, (60,)).fetchall()
        stats = conn.execute(STATS).fetchone()
        chain = conn.execute("select * from audit_verify()").fetchone()

    payload = {
        "institutions": [
            {
                "id": f"i{r['id']}",
                "pid": r["pid"],
                "name": r["name"],
                "city": r["city"],
                "state": r["state"],
                "region": r["region"],
                "address": r["address"] or "",
                "trust": r["trust"],
                "aliases": r["aliases"] or [],
            }
            for r in institutions
        ],
        "cases": [
            {
                "id": r["id"],
                "instId": r["inst_id"],
                "category": r["category"],
                "bureau": BUREAU_UI.get(r["bureau"], r["bureau"]),
                "status": r["status"],
                "received": r["received"],
                "lastAction": r["last_action"],
                "nextAction": r["next_action"],
                "lastActionDate": r["last_action_date"],
                "expected": r["expected"],
                "officer": r["officer"],
                "sla": r["sla_days"],
                "docs": r["docs"],
                "summary": r["summary"],
            }
            for r in cases
        ],
        "overlaps": [
            {
                "id": r["id"],
                "instId": r["inst_id"],
                "caseIds": r["case_ids"] or [],
                "confidence": round(r["confidence"], 1),
                "reason": r["reason"] or [],
                "state": r["state"],
                "room": r["room"],
                "lead": r["lead"],
                "detected": r["detected"],
            }
            for r in overlaps
        ],
        "rooms": {
            r["id"]: {
                "id": r["id"],
                "overlapId": r["overlap_id"],
                "lead": r["lead"],
                "custody": r["custody"],
                "escalated": r["escalated"],
                "activity": r["activity"] or [],
            }
            for r in rooms
        },
        "audit": audit_rows,
        "stats": stats,
        "chain": {"entries": chain["entries"], "ok": chain["ok"], "broken_at": chain["broken_at"]},
    }
    return JSONResponse(payload, headers={"Cache-Control": "no-store"})


@app.get("/api/meta")
def meta():
    try:
        stats = db.one(STATS)
        chain = db.one("select * from audit_verify()")
        version = db.one("select version() as v")["v"].split(" on ")[0]
    except Exception as exc:
        raise HTTPException(503, str(exc).splitlines()[0])
    return {
        "service": "ekasutra-api",
        "database": "supabase-postgres",
        "version": version,
        "stats": stats,
        "chain": {"entries": chain["entries"], "ok": chain["ok"], "broken_at": chain["broken_at"]},
        "demo": {
            "auth": False,
            "actor": "seeded demo user resolved server-side from X-Demo-Role",
            "uploads": "metadata only",
            "data": "synthetic complaints; institution names from the public AICTE master",
        },
    }


@app.get("/api/audit")
def audit_log(limit: int = 60):
    limit = max(1, min(limit, 200))
    return db.rows(AUDIT, (limit,))


@app.get("/api/audit/verify")
def audit_check():
    return db.one("select * from audit_verify()")


@app.get("/api/match")
def match(text: str, state: str | None = None, limit: int = 3):
    """The SQL matcher, for anyone comparing it with the browser's advisory layer."""
    text = text.strip()
    if len(text) < 3:
        raise HTTPException(422, "text is too short")
    limit = max(1, min(limit, 10))
    return db.rows("select * from fn_match_institution(%s, %s, %s)", (text[:200], state, limit))


@app.post("/api/cases", status_code=201)
def create_case(body: NewCase, role: str | None = Header(default=None, alias="X-Demo-Role")):
    who = actor(role)
    category = text_field(body.category, "category", 2, 80)
    summary = text_field(body.summary, "summary", 10)
    bureau = BUREAU.get(body.bureau)
    if not bureau:
        raise HTTPException(422, f"Unknown bureau {body.bureau!r}")

    with db.connection() as conn:
        with conn.transaction():
            inst = resolve_institution(conn, body.institution)
            conn.execute("select pg_advisory_xact_lock(hashtext('ekasutra.case_no'))")
            n = conn.execute(
                "select coalesce(max(regexp_replace(case_no, '^.*-', '')::int), 0) + 1 as n from cases"
            ).fetchone()["n"]
            year = conn.execute("select extract(year from current_date)::int as y").fetchone()["y"]
            case_no = f"C-{year}-{n:04d}"
            sla = SLA.get(category, 60)

            conn.execute(
                """insert into cases (case_no, institution_id, bureau, category, status,
                                      received_on, sla_days, last_action, last_action_on,
                                      next_action, expected_disposal, summary)
                   values (%s, %s, %s, %s, 'Pending', current_date, %s,
                           'Case created', current_date, 'Assign officer',
                           current_date + %s, %s)""",
                (case_no, inst["id"], bureau, category, sla, sla, summary),
            )
            conn.execute(
                """insert into case_events (case_id, actor, kind, detail)
                   select id, %s, 'created', %s from cases where case_no = %s""",
                (who["full_name"], summary, case_no),
            )
            if body.duplicateReason:
                reason = text_field(body.duplicateReason, "duplicateReason", 5, 300)
                conn.execute(
                    """insert into case_events (case_id, actor, kind, detail)
                       select id, %s, 'note', %s from cases where case_no = %s""",
                    (who["full_name"], f"Separate case created with reason: {reason}", case_no),
                )
            audit(conn, who["full_name"], "Case created from complaint email", case_no)
            return case_row(conn, case_no)


@app.post("/api/cases/{case_no}/actions")
def case_action(case_no: str, body: CaseAction, role: str | None = Header(default=None, alias="X-Demo-Role")):
    who = actor(role)
    with db.connection() as conn:
        with conn.transaction():
            row = conn.execute("select * from cases where case_no = %s for update", (case_no,)).fetchone()
            if not row:
                raise HTTPException(404, f"Case {case_no} not found")
            cid = row["id"]

            if body.type == "assign":
                officer = conn.execute("select id, full_name from users where full_name = %s", ((body.officer or "").strip(),)).fetchone()
                if not officer:
                    raise HTTPException(422, f"Unknown officer {body.officer!r}")
                status = "Under Process" if row["status"] == "Pending" else row["status"]
                conn.execute(
                    """update cases set officer_id = %s, status = %s, last_action = %s,
                              last_action_on = current_date, next_action = 'Review institution response',
                              updated_at = now()
                       where id = %s""",
                    (officer["id"], status, f"Assigned to {officer['full_name']}", cid),
                )
                conn.execute(
                    "insert into case_events (case_id, actor, kind, detail) values (%s, %s, 'assigned', %s)",
                    (cid, who["full_name"], f"Assigned to {officer['full_name']}"),
                )
                audit(conn, who["full_name"], f"Case assigned to {officer['full_name']}", case_no)

            elif body.type == "transfer":
                to = BUREAU.get(body.to or "")
                if not to:
                    raise HTTPException(422, f"Unknown bureau {body.to!r}")
                conn.execute(
                    """update cases set bureau = %s, transfer_to = %s, status = 'Transferred',
                              last_action = %s, last_action_on = current_date,
                              next_action = 'Custody acceptance pending', updated_at = now()
                       where id = %s""",
                    (to, to, f"Transferred to {BUREAU_UI[to]}", cid),
                )
                conn.execute(
                    "insert into case_events (case_id, actor, kind, detail) values (%s, %s, 'transfer', %s)",
                    (cid, who["full_name"], f"Transferred to {BUREAU_UI[to]}"),
                )
                audit(conn, who["full_name"], f"Transferred to {BUREAU_UI[to]} — custody not yet accepted", case_no)

            elif body.type == "dispose":
                reason = text_field(body.reason, "reason", 5)
                outcome = (body.outcome or "Closed — no violation").strip()[:80]
                conn.execute(
                    """update cases set status = 'Disposed', last_action = %s,
                              last_action_on = current_date, next_action = 'None — disposed',
                              expected_disposal = current_date, updated_at = now()
                       where id = %s""",
                    (f"{outcome} — {reason[:60]}", cid),
                )
                conn.execute(
                    "insert into case_events (case_id, actor, kind, detail) values (%s, %s, 'disposal', %s)",
                    (cid, who["full_name"], f"{outcome}: {reason}"),
                )
                audit(conn, who["full_name"], f"Disposed ({outcome}): {reason[:80]}", case_no)

            elif body.type == "reopen":
                conn.execute(
                    """update cases set status = 'Under Process', last_action = 'Reopened for review',
                              last_action_on = current_date, next_action = 'Review reopened record',
                              updated_at = now()
                       where id = %s""",
                    (cid,),
                )
                conn.execute(
                    "insert into case_events (case_id, actor, kind, detail) values (%s, %s, 'reopen', %s)",
                    (cid, who["full_name"], "Reopened for review"),
                )
                audit(conn, who["full_name"], "Case reopened for review", case_no)

            elif body.type == "docs":
                conn.execute(
                    """update cases set last_action = 'Documents requested from institution',
                              last_action_on = current_date, next_action = 'Await documents (7 days)',
                              updated_at = now()
                       where id = %s""",
                    (cid,),
                )
                conn.execute(
                    "insert into case_events (case_id, actor, kind, detail) values (%s, %s, 'document', %s)",
                    (cid, who["full_name"], "Documents requested from institution"),
                )
                audit(conn, who["full_name"], "Documents requested from institution", case_no)

            elif body.type == "note":
                text = text_field(body.text, "text", 2)
                conn.execute(
                    "insert into case_events (case_id, actor, kind, detail) values (%s, %s, 'note', %s)",
                    (cid, who["full_name"], text),
                )
                audit(conn, who["full_name"], f"Note added: {text[:80]}", case_no)

            else:
                raise HTTPException(422, f"Unknown action {body.type!r}")

            return case_row(conn, case_no)


@app.post("/api/overlaps/{ref}/dismiss")
def dismiss_overlap(ref: str, body: Dismiss | None = None, role: str | None = Header(default=None, alias="X-Demo-Role")):
    who = actor(role)
    with db.connection() as conn:
        with conn.transaction():
            row = conn.execute("select id, state from overlap_clusters where ref = %s for update", (ref,)).fetchone()
            if not row:
                raise HTTPException(404, f"Overlap {ref} not found")
            if row["state"] != "open":
                raise HTTPException(409, f"Overlap {ref} is already {row['state']}")
            note = (body.reason or "").strip()[:300] if body else ""
            conn.execute(
                """update overlap_clusters set state = 'dismissed', reviewed_by = %s,
                          reviewed_at = now(), review_note = nullif(%s, '')
                   where id = %s""",
                (who["id"], note, row["id"]),
            )
            audit(conn, who["full_name"], "Overlap dismissed — not the same institution", ref)
            return {"ref": ref, "state": "dismissed"}


@app.post("/api/rooms/{ref}/actions")
def room_action(ref: str, body: RoomAction, role: str | None = Header(default=None, alias="X-Demo-Role")):
    who = actor(role)
    with db.connection() as conn:
        with conn.transaction():
            room = conn.execute(
                """select r.id, r.overlap_id, r.lead_bureau, r.escalated_at, r.merged_into_case, o.ref as overlap
                   from rooms r join overlap_clusters o on o.id = r.overlap_id
                   where r.ref = %s for update of r""",
                (ref,),
            ).fetchone()
            if not room:
                raise HTTPException(404, f"Room {ref} not found")

            if body.type == "lead":
                lead = None if (body.lead or "Unassigned") in ("", "Unassigned") else BUREAU.get(body.lead or "")
                if body.lead not in ("Unassigned", "", None) and not lead:
                    raise HTTPException(422, f"Unknown bureau {body.lead!r}")
                conn.execute("update rooms set lead_bureau = %s where id = %s", (lead, room["id"]))
                label = BUREAU_UI.get(lead, "Unassigned")
                conn.execute(
                    "insert into room_activity (room_id, actor, action) values (%s, %s, %s)",
                    (room["id"], who["full_name"], f"assigned lead bureau: {label}"),
                )
                audit(conn, who["full_name"], f"Assigned lead bureau: {label}", ref)

            elif body.type == "decision":
                text = text_field(body.text, "text", 5)
                conn.execute(
                    "insert into room_activity (room_id, actor, action) values (%s, %s, %s)",
                    (room["id"], who["full_name"], f"recorded joint decision: {text[:70]}"),
                )
                audit(conn, who["full_name"], f"Joint decision recorded: {text[:80]}", ref)

            elif body.type == "docs":
                live = conn.execute(
                    """select c.id, c.case_no from cases c
                       join overlap_cases oc on oc.case_id = c.id
                       where oc.overlap_id = %s and c.status <> 'Disposed'""",
                    (room["overlap_id"],),
                ).fetchall()
                for c in live:
                    conn.execute(
                        """update cases set last_action = %s, last_action_on = current_date,
                                  next_action = 'Await documents (7 days)', updated_at = now()
                           where id = %s""",
                        (f"Documents requested (room {ref})", c["id"]),
                    )
                    conn.execute(
                        "insert into case_events (case_id, actor, kind, detail) values (%s, %s, 'document', %s)",
                        (c["id"], who["full_name"], f"Documents requested (room {ref})"),
                    )
                    audit(conn, who["full_name"], f"Documents requested from institution (room {ref})", c["case_no"])
                conn.execute(
                    "insert into room_activity (room_id, actor, action) values (%s, %s, %s)",
                    (room["id"], who["full_name"], f"requested documents for {len(live)} cases"),
                )

            elif body.type == "merge":
                overlap = conn.execute("select state from overlap_clusters where id = %s", (room["overlap_id"],)).fetchone()
                if overlap["state"] == "merged":
                    raise HTTPException(409, "Duplicates are already merged")
                linked = conn.execute(
                    """select c.id, c.case_no, c.received_on from cases c
                       join overlap_cases oc on oc.case_id = c.id
                       where oc.overlap_id = %s order by c.received_on, c.id""",
                    (room["overlap_id"],),
                ).fetchall()
                if len(linked) < 2:
                    raise HTTPException(409, "No duplicate to merge")
                lead, rest = linked[0], linked[1:]
                for c in rest:
                    conn.execute(
                        """update cases set duplicate_of = %s, status = 'Disposed',
                                  last_action = %s, last_action_on = current_date,
                                  next_action = %s, expected_disposal = current_date, updated_at = now()
                           where id = %s""",
                        (lead["id"], f"Merged as duplicate of {lead['case_no']}",
                         f"None — merged into {lead['case_no']}", c["id"]),
                    )
                    conn.execute(
                        "insert into case_events (case_id, actor, kind, detail) values (%s, %s, 'merged', %s)",
                        (c["id"], who["full_name"], f"Merged into {lead['case_no']}"),
                    )
                    audit(conn, who["full_name"], f"Merged as duplicate of {lead['case_no']}", c["case_no"])
                conn.execute(
                    """update overlap_clusters set state = 'merged', merged_into_case = %s, merged_at = now()
                       where id = %s""",
                    (lead["id"], room["overlap_id"]),
                )
                conn.execute("update rooms set merged_into_case = %s where id = %s", (lead["id"], room["id"]))
                conn.execute(
                    "insert into room_activity (room_id, actor, action) values (%s, %s, %s)",
                    (room["id"], who["full_name"],
                     "merged " + ", ".join(c["case_no"] for c in rest) + f" into {lead['case_no']}"),
                )
                return {"merged_into": lead["case_no"], "absorbed": [c["case_no"] for c in rest]}

            elif body.type == "escalate":
                reason = text_field(body.reason, "reason", 5)
                if room["escalated_at"]:
                    raise HTTPException(409, "Room is already escalated")
                live = conn.execute(
                    """select c.id, c.case_no from cases c
                       join overlap_cases oc on oc.case_id = c.id
                       where oc.overlap_id = %s and c.status <> 'Disposed'""",
                    (room["overlap_id"],),
                ).fetchall()
                if not live:
                    raise HTTPException(409, "No open cases to escalate")
                conn.execute(
                    """update rooms set escalated_at = now(), escalated_by = %s, escalation_reason = %s
                       where id = %s""",
                    (who["id"], reason, room["id"]),
                )
                for c in live:
                    conn.execute(
                        """update cases set status = 'Escalated', last_action = %s,
                                  last_action_on = current_date, next_action = 'Director review',
                                  updated_at = now()
                           where id = %s""",
                        (f"Escalated to Director (room {ref})", c["id"]),
                    )
                    conn.execute(
                        "insert into case_events (case_id, actor, kind, detail) values (%s, %s, 'escalation', %s)",
                        (c["id"], who["full_name"], f"Escalated to Director (room {ref}): {reason}"),
                    )
                    audit(conn, who["full_name"], f"Escalated to Director — {reason[:70]}", c["case_no"])
                conn.execute(
                    "insert into room_activity (room_id, actor, action) values (%s, %s, %s)",
                    (room["id"], who["full_name"],
                     f"escalated {len(live)} cases to the Director: {reason[:60]}"),
                )
                return {"escalated": [c["case_no"] for c in live], "reason": reason}

            else:
                raise HTTPException(422, f"Unknown action {body.type!r}")

            return {"ref": ref, "action": body.type, "ok": True}


if WEB.is_dir():
    app.mount("/", StaticFiles(directory=str(WEB), html=True), name="web")
