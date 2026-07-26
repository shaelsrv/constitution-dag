#!/usr/bin/env python3
"""Scaffold a new country dump from the template, or (re)stamp manifest + SHA256SUMS.

Two jobs, no dependencies (stdlib only):

  python newdump.py new <country-slug>     # copy dumps/_template -> dumps/<slug>-0.1.0
  python newdump.py stamp <dump-dir>       # regenerate manifest.json counts + SHA256SUMS

`new` gives you a validates-green skeleton (one constitution, a handful of apex
offices, one town) to edit into your own country. `stamp` is what you run after
every edit so `validate.py` passes — it recomputes the row counts and checksums
for you, so you never hand-maintain them.

Typical first session:

  python newdump.py new riverland
  # ... edit dumps/riverland-0.1.0/*.jsonl to your real country ...
  python newdump.py stamp dumps/riverland-0.1.0
  python validate.py dumps/riverland-0.1.0
  python dag.py dumps/riverland-0.1.0 paths <your-town>
"""

import hashlib
import json
import os
import shutil
import sys

# Every table dag.py / validate.py may read. A dump needs all of them present
# (empty is fine) so a missing-file typo can't masquerade as missing data.
TABLES = [
    "nations", "jurisdictions", "legal_instruments", "instrument_edges",
    "constitutional_controls", "division_kind_grants", "domain_allocations",
    "citizen_rights", "positions", "divisions", "places", "place_divisions",
    "position_divisions", "position_domains", "dependencies",
]


def stamp(dump):
    if not os.path.isdir(dump):
        sys.exit(f"not a directory: {dump}")
    counts = {}
    for fn in sorted(os.listdir(dump)):
        if fn.endswith(".jsonl"):
            with open(os.path.join(dump, fn), encoding="utf-8") as f:
                counts[fn[:-6]] = sum(1 for line in f if line.strip())
    # preserve version/nations/license if a manifest already exists
    mpath = os.path.join(dump, "manifest.json")
    prev = json.load(open(mpath, encoding="utf-8")) if os.path.exists(mpath) else {}
    manifest = {
        "format": "constitution-dag-dump/1",
        "version": prev.get("version", os.path.basename(dump.rstrip("/\\")).rsplit("-", 1)[-1] or "0.1.0"),
        "nations": prev.get("nations", []),
        "license": prev.get("license", "CC-BY-4.0"),
        "counts": counts,
        "provenance_note": prev.get("provenance_note",
                                    "built with newdump.py; verify every row against primary sources"),
    }
    json.dump(manifest, open(mpath, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    lines = []
    for fn in sorted(os.listdir(dump)):
        if fn == "SHA256SUMS":
            continue
        p = os.path.join(dump, fn)
        if os.path.isfile(p):
            lines.append(f"{hashlib.sha256(open(p, 'rb').read()).hexdigest()}  {fn}")
    with open(os.path.join(dump, "SHA256SUMS"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print(f"stamped {dump}: {sum(counts.values())} rows across {len(counts)} tables")


def new(slug):
    template = os.path.join("dumps", "_template")
    if not os.path.isdir(template):
        sys.exit("dumps/_template not found — are you in the repo root?")
    dest = os.path.join("dumps", f"{slug}-0.1.0")
    if os.path.exists(dest):
        sys.exit(f"{dest} already exists — pick another slug or delete it")
    shutil.copytree(template, dest)
    # ensure every table file exists (empty if the template omitted it)
    for t in TABLES:
        p = os.path.join(dest, t + ".jsonl")
        if not os.path.exists(p):
            open(p, "w", encoding="utf-8").close()
    stamp(dest)
    print(f"\ncreated {dest} — a validates-green skeleton.")
    print("next: edit the .jsonl files to your country, then:")
    print(f"  python newdump.py stamp {dest}")
    print(f"  python validate.py {dest}")


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("new", "stamp"):
        print(__doc__)
        sys.exit(1)
    (new if sys.argv[1] == "new" else stamp)(sys.argv[2])


if __name__ == "__main__":
    main()
