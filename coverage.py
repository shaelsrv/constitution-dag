#!/usr/bin/env python3
"""constitution-dag coverage census — how much of the real role-space we hold.

The map is always incomplete; this makes the incompleteness MEASURABLE instead
of vague. Reports, per dump:

  depth       offices per state jurisdiction (which states are real vs token)
  templates   repeating office-name templates (e.g. 'District Magistrate, X')
              and how many instances exist — the gap between instances-held and
              the ~750 districts / thousands of municipalities that exist in
              reality is the honest backlog
  bare kinds  division kinds present with zero serving offices
  grounding   offices with no instrument grant (per nation)

Usage:  python coverage.py dumps/india-0.12.0
Exit 0 always — this is a census, not a gate.
"""

import json
import os
import re
import sys
from collections import Counter, defaultdict


def load(dumpdir):
    d = {}
    for name in os.listdir(dumpdir):
        if name.endswith(".jsonl"):
            with open(os.path.join(dumpdir, name), encoding="utf-8") as f:
                d[name[:-6]] = [json.loads(x) for x in f if x.strip()]
    return d


# strip the place/instance part of an office name to find its TEMPLATE
def template(name):
    t = re.split(r"[,(]", name)[0].strip()
    t = re.sub(r"\b(of|for)\s+[A-Z][\w. ]+$", "", t).strip()
    return t


def main():
    d = load(sys.argv[1])
    live = [p for p in d["positions"] if not p.get("deprecated_at")]
    jur = {j["id"]: j for j in d["jurisdictions"]}

    print(f"coverage census: {sys.argv[1]}")
    print(f"  offices (live): {len(live)}   places: {len(d['places'])}   "
          f"divisions: {len(d['divisions'])}\n")

    # depth per state jurisdiction
    per_state = Counter()
    for p in live:
        j = jur.get(p.get("jurisdiction_id"))
        while j and j.get("level") not in ("state", "national", None):
            j = jur.get(j.get("parent_id"))
        key = (j.get("name") if j and j.get("level") == "state" else "(national/other)")
        per_state[key] += 1
    print("  DEPTH — offices per state jurisdiction:")
    for name, n in per_state.most_common():
        print(f"    {n:5d}  {name}")

    # templates
    tmpl = defaultdict(list)
    for p in live:
        tmpl[template(p["name"])].append(p)
    repeating = {k: v for k, v in tmpl.items() if len(v) >= 3}
    print(f"\n  TEMPLATES — {len(tmpl)} distinct office templates; "
          f"{len(repeating)} repeat 3+ times (instantiable patterns):")
    for k, v in sorted(repeating.items(), key=lambda kv: -len(kv[1]))[:15]:
        print(f"    {len(v):4d}x  {k}")
    print("    (each repeating template is a per-district/per-city pattern —")
    print("     ~750 districts and thousands of municipalities exist in reality;")
    print("     instances-held vs that number is the honest backlog)")

    # bare division kinds
    served = {r["division_id"] for r in d["position_divisions"]}
    bare = Counter(v["kind"] for v in d["divisions"] if v["id"] not in served)
    if bare:
        print("\n  BARE — division kinds with instances but zero serving offices:")
        for k, n in bare.most_common():
            print(f"    {n:4d}  {k}")

    # grounding
    granted = {e["position_id"] for e in d["instrument_edges"]
               if e["relation"] in ("created_by", "empowered_by")}
    ungrounded = [p for p in live if p["id"] not in granted]
    print(f"\n  GROUNDING — {len(granted & {p['id'] for p in live})} offices "
          f"instrument-granted; {len(ungrounded)} without any grant "
          f"({100*len(ungrounded)//max(1,len(live))}% of the dump) — the "
          "constitutional-genealogy backlog.")


if __name__ == "__main__":
    main()
