#!/usr/bin/env python3
"""Generate seed_demo.sql from demo_seed.json.

Deterministic: same JSON in, byte-identical SQL out. The audit chain is hashed
here with the exact formula used by audit_write() and audit_verify():

    sha256(prev_hash || to_char(at at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.US')
           || actor || action || object)

Run:  python3 generate_demo_seed.py
"""
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEED = json.loads((HERE / "demo_seed.json").read_text(encoding="utf-8"))

USERS = [
    # email, full name, role, bureau
    ("r.menon@aicte.gov.in", "R. Menon", "lead", "RB"),
    ("p.rao@aicte.gov.in", "P. Rao", "officer", "PGRC"),
    ("k.nair@aicte.gov.in", "K. Nair", "officer", "RB"),
    ("a.das@aicte.gov.in", "A. Das", "officer", "PGRC"),
    ("a.kumar@aicte.gov.in", "A. Kumar", "officer", "PGRC"),
    ("s.iyer@aicte.gov.in", "S. Iyer", "officer", "RO"),
    ("m.das@aicte.gov.in", "M. Das", "officer", "RO"),
    ("director@aicte.gov.in", "Director, AICTE", "director", None),
    ("admin@aicte.gov.in", "System Administrator", "admin", None),
]

BUREAU = {"RB": "RB", "PGRC": "PGRC", "Regional Office": "RO", "RO": "RO"}
DETECTED = {
    "CL-01": "2026-10-20 10:38:00+00",
    "CL-02": "2026-10-19 15:10:00+00",
    "CL-03": "2026-10-21 09:12:00+00",
}
OPENED = {
    "CR-01": "2026-10-20 10:45:00+00",
    "CR-02": "2026-10-19 15:12:00+00",
    "CR-03": "2026-10-21 09:20:00+00",
}
DOC_NAMES = [
    "complaint.pdf",
    "annexure-a.pdf",
    "institution-response.pdf",
    "inspection-note.pdf",
    "fee-ledger.pdf",
    "attendance-register.pdf",
    "correspondence.pdf",
]
ESCALATION = {
    "case_no": "C-2026-0186",
    "at": "2026-10-21 09:15:00+00",
    "actor": "System",
    "kind": "escalation",
    "detail": "Custody not accepted — escalated to Director",
}


def lit(value):
    if value is None:
        return "null"
    return "'" + str(value).replace("'", "''") + "'"


def chain_head(rows):
    prev = "0" * 64
    for entry in reversed(rows):  # JSON is newest-first
        at = datetime.strptime(entry["time"], "%Y-%m-%d %H:%M")
        stamp = at.strftime("%Y-%m-%dT%H:%M:%S.000000")
        digest = hashlib.sha256(
            (prev + stamp + entry["actor"] + entry["action"] + entry["obj"]).encode("utf-8")
        ).hexdigest()
        prev = digest
    return prev


def case_rows():
    out = []
    for c in SEED["cases"]:
        institution = next(i for i in SEED["institutions"] if i["id"] == c["instId"])
        officer = None if c["officer"] == "Unassigned" else c["officer"]
        transfer_to = "PGRC" if c["id"] == "C-2026-0186" else None
        out.append(
            "({}, {}, {}, {}, {}, {}, {}::date, {}::int, {}, {}, {}::date, {}, {}::date, {})".format(
                lit(c["id"]),
                lit(institution["pid"]),
                lit(BUREAU[c["bureau"]]),
                lit(c["category"]),
                lit(c["status"]),
                lit(transfer_to),
                lit(c["received"]),
                lit(c["sla"]),
                lit(officer),
                lit(c["lastAction"]),
                lit(c["lastActionDate"]),
                lit(c["nextAction"]),
                lit(c["expected"]),
                lit(c["summary"]),
            )
        )
    return out


def event_rows():
    rows = []
    for c in SEED["cases"]:
        received = datetime.strptime(c["received"], "%Y-%m-%d")
        assigned = c["officer"] != "Unassigned"
        lead = "P. Rao" if c["bureau"] == "PGRC" else "R. Menon"
        if c["bureau"] == "Regional Office":
            lead = "M. Das"
        officer = c["officer"] if assigned else lead
        tail_kind = {
            "Disposed": "disposal",
            "Transferred": "transfer",
            "Escalated": "escalation",
        }.get(c["status"], "note")
        rows += [
            (
                c["id"],
                (received + timedelta(hours=9, minutes=30)).strftime("%Y-%m-%d %H:%M:%S+00"),
                "System",
                "created",
                "Case created from complaint",
            ),
            (
                c["id"],
                (received + timedelta(hours=10, minutes=30)).strftime("%Y-%m-%d %H:%M:%S+00"),
                officer,
                "document",
                "{} document(s) uploaded and hashed (SHA-256)".format(c["docs"]),
            ),
            (
                c["id"],
                (received + timedelta(hours=11, minutes=15)).strftime("%Y-%m-%d %H:%M:%S+00"),
                lead,
                "assigned" if assigned else "note",
                "Assigned to {} · {}".format(c["officer"], BUREAU[c["bureau"]])
                if assigned
                else "Unassigned — queued for {} lead".format(BUREAU[c["bureau"]]),
            ),
            (
                c["id"],
                c["lastActionDate"] + " 15:30:00+00",
                officer,
                tail_kind,
                c["lastAction"],
            ),
        ]
    rows.append(
        (
            ESCALATION["case_no"],
            ESCALATION["at"],
            ESCALATION["actor"],
            ESCALATION["kind"],
            ESCALATION["detail"],
        )
    )
    return rows


def document_rows():
    rows = []
    for c in SEED["cases"]:
        received = datetime.strptime(c["received"], "%Y-%m-%d")
        officer = None if c["officer"] == "Unassigned" else c["officer"]
        for n in range(1, c["docs"] + 1):
            base = DOC_NAMES[(n - 1) % len(DOC_NAMES)]
            if n > len(DOC_NAMES):
                base = "evidence-{:02d}.pdf".format(n)
            filename = "{}_{:02d}_{}".format(c["id"].lower(), n, base)
            digest = hashlib.sha256(
                "{}|{}|{}".format(c["id"], n, filename).encode("utf-8")
            ).hexdigest()
            size = 60000 + int(digest[:8], 16) % 2400000
            uploaded = received + timedelta(days=min(n, 6), minutes=n)
            rows.append(
                (
                    c["id"],
                    filename,
                    "application/pdf",
                    size,
                    digest,
                    "demo/{}/{:02d}-{}".format(c["id"], n, base),
                    officer,
                    uploaded.strftime("%Y-%m-%d %H:%M:%S+00"),
                )
            )
    return rows


def overlap_reason(overlap):
    return json.dumps(overlap["reason"], ensure_ascii=False).replace("'", "''")


def room_activity_rows():
    rows = []
    for ref in sorted(SEED["rooms"]):
        for a in SEED["rooms"][ref]["activity"]:
            stamp = datetime.strptime("2026 " + a["t"], "%Y %d %b %H:%M")
            rows.append(
                (
                    ref,
                    stamp.strftime("%Y-%m-%d %H:%M:00+00"),
                    a["a"],
                    a["x"],
                )
            )
    return rows


def audit_rows():
    prev = "0" * 64
    rows = []
    for entry in reversed(SEED["audit"]):
        at = datetime.strptime(entry["time"], "%Y-%m-%d %H:%M")
        stamp = at.strftime("%Y-%m-%dT%H:%M:%S.000000")
        digest = hashlib.sha256(
            (prev + stamp + entry["actor"] + entry["action"] + entry["obj"]).encode("utf-8")
        ).hexdigest()
        rows.append(
            (
                at.strftime("%Y-%m-%d %H:%M:%S+00"),
                entry["actor"],
                entry["action"],
                entry["obj"],
                prev,
                digest,
            )
        )
        prev = digest
    return rows


def build_sql():
    events = event_rows()
    documents = document_rows()
    activities = room_activity_rows()
    audit = audit_rows()
    head = chain_head(SEED["audit"])

    institutions = SEED["institutions"]
    cases = SEED["cases"]
    overlaps = SEED["overlaps"]
    rooms = SEED["rooms"]
    alias_rows = [
        (i["pid"], alias, ["master", "complaint", "manual"][n % 3])
        for i in institutions
        for n, alias in enumerate(i["aliases"])
    ]

    parts = []
    add = parts.append

    add("-- ============================================================================")
    add("-- Ekasutra · SIH26264 · demo seed (generated, do not edit by hand)")
    add("--")
    add("-- Source : demo_seed.json  ·  generator: generate_demo_seed.py")
    add("-- Target : PostgreSQL 14+ with schema.sql already loaded")
    add("-- Rows   : {} institutions, {} aliases, {} users, {} cases,".format(
        len(institutions), len(alias_rows), len(USERS), len(cases)))
    add("--          {} case events, {} documents, {} overlap clusters,".format(
        len(events), len(documents), len(overlaps)))
    add("--          {} overlap-case links, {} rooms, {} room activities,".format(
        sum(len(o["caseIds"]) for o in overlaps), len(rooms), len(activities)))
    add("--          {} audit entries".format(len(audit)))
    add("--")
    add("-- Chain  : genesis = 64 zeros · head =")
    add("--          " + head)
    add("--")
    add("-- Load into an EMPTY database only. The guard below refuses to touch a")
    add("-- database that already has institutions, cases or audit rows, so this")
    add("-- file can never overwrite the 9,558-row national master.")
    add("--")
    add("--   createdb ekasutra_demo")
    add("--   psql -d ekasutra_demo -f schema.sql")
    add("--   psql -d ekasutra_demo -f seed_demo.sql")
    add("-- ============================================================================")
    add("")
    add("\\set ON_ERROR_STOP on")
    add("")
    add("-- The audit hashes are computed over UTF-8 bytes. Force the client encoding")
    add("-- so a Windows psql session cannot transcode '→' into mojibake before hashing.")
    add("set client_encoding = 'utf8';")
    add("")
    add("begin;")
    add("")
    add("do $$")
    add("begin")
    add("  if (select count(*) from institutions) <> 0")
    add("     or (select count(*) from users) <> 0")
    add("     or (select count(*) from cases) <> 0")
    add("     or (select count(*) from audit_entries) <> 0 then")
    add("    raise exception 'seed_demo.sql: target database is not empty. Create a fresh database, e.g. createdb ekasutra_demo';")
    add("  end if;")
    add("end $$;")
    add("")
    add("-- ------------------------------------------------------------------- users")
    add("insert into users (email, full_name, role, bureau) values")
    add(",\n".join(
        "  ({}, {}, {}, {})".format(lit(e), lit(n), lit(r), lit(b)) for e, n, r, b in USERS
    ) + ";")
    add("")
    add("-- ------------------------------------------------------------ institutions")
    add("insert into institutions (permanent_id, name, address, city, state, region, trust_name) values")
    add(",\n".join(
        "  ({}, {}, {}, {}, {}, {}, {})".format(
            lit(i["pid"]), lit(i["name"]), lit(i["address"]), lit(i["city"]),
            lit(i["state"]), lit(i["region"]), lit(i["trust"])
        )
        for i in institutions
    ) + ";")
    add("")
    add("insert into institution_aliases (institution_id, alias, source)")
    add("select i.id, v.alias, v.source")
    add("from (values")
    add(",\n".join(
        "  ({}, {}, {})".format(lit(pid), lit(alias), lit(source))
        for pid, alias, source in alias_rows
    ) + ") as v(pid, alias, source)")
    add("join institutions i on i.permanent_id = v.pid;")
    add("")
    add("-- ------------------------------------------------------------------- cases")
    add("insert into cases (case_no, institution_id, bureau, category, status, transfer_to,")
    add("                   received_on, sla_days, officer_id, last_action, last_action_on,")
    add("                   next_action, expected_disposal, summary)")
    add("select v.case_no, i.id, v.bureau, v.category, v.status, v.transfer_to,")
    add("       v.received_on::date, v.sla_days::int, u.id, v.last_action,")
    add("       v.last_action_on::date, v.next_action, v.expected::date, v.summary")
    add("from (values")
    add(",\n".join("  " + r for r in case_rows()) + ")")
    add("as v(case_no, pid, bureau, category, status, transfer_to, received_on, sla_days,")
    add("     officer, last_action, last_action_on, next_action, expected, summary)")
    add("join institutions i on i.permanent_id = v.pid")
    add("left join users u on u.full_name = v.officer;")
    add("")
    add("-- -------------------------------------------------------------- case events")
    add("insert into case_events (case_id, at, actor, kind, detail)")
    add("select c.id, v.at::timestamptz, v.actor, v.kind, v.detail")
    add("from (values")
    add(",\n".join(
        "  ({}, {}::timestamptz, {}, {}, {})".format(
            lit(case_no), lit(at), lit(actor), lit(kind), lit(detail)
        )
        for case_no, at, actor, kind, detail in events
    ) + ") as v(case_no, at, actor, kind, detail)")
    add("join cases c on c.case_no = v.case_no;")
    add("")
    add("-- ---------------------------------------------------------------- documents")
    add("insert into documents (case_id, filename, mime, bytes, sha256, storage_key,")
    add("                       uploaded_by, uploaded_at)")
    add("select c.id, v.filename, v.mime, v.bytes::bigint, v.sha, v.key, u.id,")
    add("       v.at::timestamptz")
    add("from (values")
    add(",\n".join(
        "  ({}, {}, {}, {}::bigint, {}, {}, {}, {}::timestamptz)".format(
            lit(case_no), lit(filename), lit(mime), lit(size), lit(digest),
            lit(key), lit(officer), lit(at)
        )
        for case_no, filename, mime, size, digest, key, officer, at in documents
    ) + ") as v(case_no, filename, mime, bytes, sha, key, officer, at)")
    add("join cases c on c.case_no = v.case_no")
    add("left join users u on u.full_name = v.officer;")
    add("")
    add("-- ------------------------------------------------------- overlap clusters")
    add("insert into overlap_clusters (ref, institution_id, confidence, state, reason, detected_at)")
    add("select v.ref, i.id, v.confidence::numeric, v.state, v.reason::jsonb,")
    add("       v.detected_at::timestamptz")
    add("from (values")
    add(",\n".join(
        "  ({}, {}, {}::numeric, {}, {}::jsonb, {}::timestamptz)".format(
            lit(o["id"]), lit(next(i["pid"] for i in institutions if i["id"] == o["instId"])),
            lit(o["confidence"]), lit(o["state"]), lit(overlap_reason(o)),
            lit(DETECTED[o["id"]])
        )
        for o in overlaps
    ) + ") as v(ref, pid, confidence, state, reason, detected_at)")
    add("join institutions i on i.permanent_id = v.pid;")
    add("")
    add("insert into overlap_cases (overlap_id, case_id)")
    add("select o.id, c.id")
    add("from (values")
    add(",\n".join(
        "  ({}, {})".format(lit(o["id"]), lit(cid))
        for o in overlaps for cid in o["caseIds"]
    ) + ") as v(ref, case_no)")
    add("join overlap_clusters o on o.ref = v.ref")
    add("join cases c on c.case_no = v.case_no;")
    add("")
    add("-- ------------------------------------------------------------------- rooms")
    add("insert into rooms (ref, overlap_id, lead_bureau, custody, state, opened_at)")
    add("select v.ref, o.id, v.lead_bureau, v.custody, 'open', v.opened_at::timestamptz")
    add("from (values")
    add(",\n".join(
        "  ({}, {}, {}::text, {}, {}::timestamptz)".format(
            lit(ref), lit(room["overlapId"]),
            lit(None if room["lead"] == "Unassigned" else BUREAU[room["lead"]]),
            lit(room["custody"]), lit(OPENED[ref])
        )
        for ref, room in sorted(rooms.items())
    ) + ") as v(ref, overlap_ref, lead_bureau, custody, opened_at)")
    add("join overlap_clusters o on o.ref = v.overlap_ref;")
    add("")
    add("insert into room_activity (room_id, at, actor, action)")
    add("select r.id, v.at::timestamptz, v.actor, v.action")
    add("from (values")
    add(",\n".join(
        "  ({}, {}::timestamptz, {}, {})".format(lit(ref), lit(at), lit(actor), lit(action))
        for ref, at, actor, action in activities
    ) + ") as v(ref, at, actor, action)")
    add("join rooms r on r.ref = v.ref;")
    add("")
    add("-- ------------------------------------------------------------- audit chain")
    add("-- Oldest first. Each row commits to the hash of the row above it.")
    add("insert into audit_entries (at, actor, action, object, prev_hash, hash) values")
    add(",\n".join(
        "  ({}::timestamptz, {}, {}, {}, {}, {})".format(
            lit(at), lit(actor), lit(action), lit(obj), lit(prev), lit(digest)
        )
        for at, actor, action, obj, prev, digest in audit
    ) + ";")
    add("")
    add("commit;")
    add("")
    add("analyze;")
    add("")
    add("-- ---------------------------------------------------------------- verify")
    add("select 'institutions' as table_name, count(*) as row_count from institutions")
    add("union all select 'institution_aliases', count(*) from institution_aliases")
    add("union all select 'users', count(*) from users")
    add("union all select 'cases', count(*) from cases")
    add("union all select 'case_events', count(*) from case_events")
    add("union all select 'documents', count(*) from documents")
    add("union all select 'overlap_clusters', count(*) from overlap_clusters")
    add("union all select 'overlap_cases', count(*) from overlap_cases")
    add("union all select 'rooms', count(*) from rooms")
    add("union all select 'room_activity', count(*) from room_activity")
    add("union all select 'audit_entries', count(*) from audit_entries")
    add("order by table_name;")
    add("")
    add("select * from audit_verify();")
    add("")
    add("-- This hash must equal the one shown on the Data Layer screen.")
    add("select hash as chain_head from audit_entries order by id desc limit 1;")
    add("")
    return "\n".join(parts)


def main():
    sql = build_sql()
    out = HERE / "seed_demo.sql"
    out.write_text(sql, encoding="utf-8")
    print("wrote", out, len(sql), "bytes")
    print("chain head", chain_head(SEED["audit"]))
    print("counts: cases", len(SEED["cases"]),
          "| events", len(event_rows()),
          "| documents", len(document_rows()),
          "| rooms", len(SEED["rooms"]),
          "| room_activity", len(room_activity_rows()))


if __name__ == "__main__":
    main()
