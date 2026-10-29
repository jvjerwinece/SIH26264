#!/usr/bin/env python3
"""Concatenate schema.sql + seed_demo.sql into pasteable Supabase files.

The Supabase SQL editor cannot run psql meta-commands, so `\\set` lines are
dropped. Everything else is copied verbatim: schema.sql stays the single
source of truth for the tables and functions.

Two outputs:
  database/Ekasutra_Supabase.sql        fresh project (schema + seed)
  database/Ekasutra_Supabase_Reset.sql  existing project (truncate + seed)
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "database" / "Ekasutra_Supabase.sql"
RESET_OUT = ROOT / "database" / "Ekasutra_Supabase_Reset.sql"

HEADER = """\
-- ============================================================================
-- Ekasutra · SIH26264 · Supabase bootstrap
--
-- GENERATED FILE — do not edit. Rebuild with:
--   python tools/build_supabase_bundle.py
-- Source: database/schema.sql + database/seed_demo.sql
--
-- How to load
--   1. Create a Supabase project (Postgres 15+).
--   2. Open SQL Editor → New query → paste this whole file → Run.
--   3. Read the final result row: 32 cases, 18 audit rows, chain_ok = true.
--
-- The seed guard refuses to run on a non-empty database, so re-running this
-- file on a populated project fails instead of overwriting live rows.
-- ============================================================================

"""

RESET_HEADER = """\
-- ============================================================================
-- Ekasutra · SIH26264 · Supabase demo reset
--
-- GENERATED FILE — do not edit. Rebuild with:
--   python tools/build_supabase_bundle.py
--
-- Use this only on the demo project, with schema.sql already loaded. It
-- truncates every demo table and reloads the deterministic seed. Any case
-- created through the API is deleted. Do not run it on the national master.
--
--   1. Open SQL Editor → New query → paste this whole file → Run.
--   2. Expect: 32 cases, 18 audit rows, chain_ok = true.
-- ============================================================================

"""

TRUNCATE = """\
truncate table audit_entries, room_activity, rooms, overlap_cases,
               overlap_clusters, documents, case_events, cases, users,
               institution_aliases, institutions
  restart identity cascade;
"""

VERIFY = """\

-- Verification: expect 32 cases, 18 audit rows, chain_ok = true.
select (select count(*) from cases)          as cases,
       (select count(*) from audit_entries)  as audit_rows,
       (select ok from audit_verify())       as chain_ok,
       (select hash from audit_entries order by id desc limit 1) as chain_head;
"""


def strip_meta(sql: str) -> str:
    return "\n".join(line for line in sql.splitlines() if not line.lstrip().startswith("\\"))


def main() -> None:
    schema = strip_meta((ROOT / "database" / "schema.sql").read_text(encoding="utf-8"))
    seed = strip_meta((ROOT / "database" / "seed_demo.sql").read_text(encoding="utf-8"))

    OUT.write_text(
        HEADER + schema.rstrip() + "\n\n" + seed.rstrip() + VERIFY,
        encoding="utf-8",
    )
    RESET_OUT.write_text(
        RESET_HEADER + TRUNCATE + "\n" + seed.rstrip() + VERIFY,
        encoding="utf-8",
    )
    for path in (OUT, RESET_OUT):
        print(f"wrote {path.relative_to(ROOT)} ({path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
