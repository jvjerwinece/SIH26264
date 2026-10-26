#!/usr/bin/env python3
"""
Ekasutra · SIH26264 — build institutions.csv from the public AICTE list.

Two inputs are supported:

  institutions.json   reviewed extract of the public AICTE approved-institutions
                      list (id, name, state, rest). This is what produced the
                      9,558 rows used in the appendix.

  aicte.txt           raw `pdftotext -layout` output. Best-effort parser for the
                      same list: handles the common single-line rows and joins
                      wrapped institution names. Review the output before load.

Usage
  python3 seed_institutions.py institutions.json institutions.csv
  python3 seed_institutions.py aicte.txt institutions.csv

Load
  createdb ekasutra && psql -d ekasutra -f schema.sql
  psql -d ekasutra -c "\\copy institutions(permanent_id,name,city,state) \
        from 'institutions.csv' csv"
"""

import csv
import json
import re
import sys

ID_RE = re.compile(r"^(\d-\d{6,10})\s{2,}(.+)$")
SPLIT_RE = re.compile(r"\s{2,}")

STATES = {
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa",
    "Gujarat", "Haryana", "Himachal Pradesh", "Jammu and Kashmir", "Jharkhand",
    "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
    "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli",
    "Daman and Diu", "Delhi", "Lakshadweep", "Puducherry",
}


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "")).strip()


def from_json(path: str):
    for row in json.load(open(path, encoding="utf-8")):
        yield (row["id"].strip(), clean(row["name"]),
               clean(row.get("rest", "")).title(), clean(row.get("state", "")))


def from_text(path: str):
    """Parse `pdftotext -layout` output. Rows look like:

    1-702730101   HSB POLYTECHNIC        West Bengal   BIRBHUM   SURI

    Long names wrap: the continuation line starts either with the rest of the
    name, or with the state column. We join until a known state appears.
    """
    name = pid = state = None
    district = city = ""

    def flush():
        if pid and name:
            yield pid, clean(name), clean(city or district), clean(state)

    for raw in open(path, encoding="utf-8", errors="ignore"):
        line = raw.rstrip("\n")
        m = ID_RE.match(line)
        if m:
            yield from flush()
            pid, rest = m.group(1), m.group(2)
            parts = SPLIT_RE.split(rest)
            # pull the state column out of the tail
            idx = next((i for i, p in enumerate(parts) if p in STATES), None)
            if idx is not None:
                name = " ".join(parts[:idx]) or parts[0]
                state = parts[idx]
                district = parts[idx + 1] if len(parts) > idx + 1 else ""
                city = parts[idx + 2] if len(parts) > idx + 2 else ""
            else:
                name, state, district, city = rest, None, "", ""
            continue

        if pid and state is None:
            cont = line.strip()
            idx = next((s for s in STATES if cont.startswith(s)), None)
            if idx:
                tail = SPLIT_RE.split(cont)
                state = tail[0]
                district = tail[1] if len(tail) > 1 else ""
                city = tail[2] if len(tail) > 2 else ""
            elif cont:
                name = f"{name} {cont}"
    yield from flush()


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2

    src, dst = sys.argv[1], sys.argv[2]
    reader = from_json(src) if src.lower().endswith(".json") else from_text(src)

    seen, rows = set(), []
    for pid, name, city, state in reader:
        if not pid or not name or pid in seen:
            continue
        seen.add(pid)
        rows.append((pid, name, city, state))

    with open(dst, "w", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerows(rows)

    print(f"{len(rows):,} institutions written to {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
