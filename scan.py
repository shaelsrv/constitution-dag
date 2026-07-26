#!/usr/bin/env python3
"""constitution-dag tripwire scanner — finds LIKELY inaccuracies (layer 2).

validate.py catches structural breakage; this catches rows that are valid but
suspicious — the contradiction classes that produced real errors in the pilot.
Output is a triage report, not a verdict: every hit needs retrieval-based
verification before it becomes a correction (see QUALITY.md, "life of an error").

  duplicates      two live offices with the same (nation, name) — merge candidates
  division bleed  a place inside >1 division of the same EXCLUSIVE kind
                  (the "Kotdwar in 14 assembly constituencies" class)
  unwatched       controllers nobody controls (open feedback loops)
  grounding gap   offices serving a pivot place with no constitutional path
  proxy drift     chamber-power mechanisms (impeach/no_confidence/assent) whose
                  note does not state the body-proxy convention
  orphan grants   instruments granting power but unreachable from any root

Usage:  python scan.py dumps/india-0.12.0 [--pivot kotdwar]
Exit 0 always (triage, not a gate); release process attaches this report.
"""

import json
import os
import sys
from collections import defaultdict

EXCLUSIVE_KINDS = {"municipal", "district", "state", "national",
                   "electoral_assembly", "electoral_house"}
CHAMBER_MECHS = {"impeach", "no_confidence", "assent"}


def load(dumpdir):
    d = {}
    for name in os.listdir(dumpdir):
        if name.endswith(".jsonl"):
            with open(os.path.join(dumpdir, name), encoding="utf-8") as f:
                d[name[:-6]] = [json.loads(x) for x in f if x.strip()]
    return d


def main():
    dumpdir = sys.argv[1]
    pivot = sys.argv[sys.argv.index("--pivot") + 1] if "--pivot" in sys.argv else None
    d = load(dumpdir)
    hits = 0

    def report(cls, msg):
        nonlocal hits
        hits += 1
        print(f"  [{cls}] {msg}")

    print(f"tripwire scan: {dumpdir}\n")

    # duplicates
    live = [p for p in d["positions"] if not p.get("deprecated_at")]
    by_name = defaultdict(list)
    for p in live:
        by_name[(p["nation_id"], p["name"].strip().lower())].append(p["slug"])
    for (_, name), slugs in sorted(by_name.items()):
        if len(slugs) > 1:
            report("duplicate", f"'{name}' held by {len(slugs)} live offices: "
                   f"{', '.join(slugs)}")

    # division bleed
    div = {v["id"]: v for v in d["divisions"]}
    pl_divs = defaultdict(list)
    for r in d["place_divisions"]:
        pl_divs[r["place_id"]].append(r["division_id"])
    places = {p["id"]: p for p in d["places"]}
    for pid, dvs in pl_divs.items():
        kinds = defaultdict(list)
        for dv in dvs:
            if dv in div and div[dv]["kind"] in EXCLUSIVE_KINDS:
                kinds[div[dv]["kind"]].append(div[dv]["name"])
        for kind, names in kinds.items():
            if len(names) > 1:
                report("division-bleed",
                       f"place '{places[pid]['slug']}' sits in {len(names)} "
                       f"'{kind}' divisions: {', '.join(sorted(names)[:5])}")

    # unwatched watchers
    controllers = {c["controller_id"] for c in d["constitutional_controls"]}
    controlled = {c["controlled_id"] for c in d["constitutional_controls"]}
    pos = {p["id"]: p for p in d["positions"]}
    for pid in sorted(controllers - controlled):
        if pid in pos:
            report("unwatched-watcher",
                   f"{pos[pid]['name']} controls others but nothing controls it")

    # grounding gap for the pivot
    if pivot:
        pl = next((p for p in d["places"] if p["slug"] == pivot), None)
        if pl:
            dvs = set(pl_divs.get(pl["id"], []))
            serving = {r["position_id"] for r in d["position_divisions"]
                       if r["division_id"] in dvs}
            granted = {e["position_id"] for e in d["instrument_edges"]
                       if e["relation"] in ("created_by", "empowered_by")}
            deps = defaultdict(set)
            for r in d["dependencies"]:
                deps[r["dependent_id"]].add(r["provider_id"])
            reachable = set()
            for s in serving:
                frontier, seen = [s], set()
                while frontier:
                    x = frontier.pop()
                    if x in seen:
                        continue
                    seen.add(x)
                    if x in granted:
                        reachable.add(s)
                        break
                    frontier.extend(deps.get(x, ()))
            for s in sorted(serving - reachable):
                if s in pos and not pos[s].get("deprecated_at"):
                    report("grounding-gap",
                           f"{pos[s]['name']} serves {pivot} with no "
                           "constitutional path")

    # proxy drift
    for c in d["constitutional_controls"]:
        if c["mechanism"] in CHAMBER_MECHS and "anchor" not in (c.get("note") or "").lower():
            a = pos.get(c["controller_id"], {}).get("name", "?")
            b = pos.get(c["controlled_id"], {}).get("name", "?")
            report("proxy-drift",
                   f"{c['mechanism']} edge {a} -> {b} lacks a body-proxy note "
                   "(chamber powers must state their anchoring)")

    # orphan grants: instrument grants power but no chain to a root
    instr = {i["id"]: i for i in d["legal_instruments"]}
    granted_by = {e["instrument_id"] for e in d["instrument_edges"]}
    roots = {i["id"] for i in d["legal_instruments"]
             if i["kind"] in ("constitution", "convention")}
    for iid in sorted(granted_by):
        cur, seen = iid, set()
        while cur and cur not in seen:
            seen.add(cur)
            if cur in roots:
                break
            cur = instr.get(cur, {}).get("amends_id")
        else:
            k = instr.get(iid, {}).get("kind")
            if k not in ("statute", "order", "charter", "court_decision"):
                report("orphan-grant",
                       f"instrument '{instr.get(iid, {}).get('title')}' grants "
                       "power but chains to no constitutional root")

    print(f"\n{hits} tripwire hit(s) — each needs retrieval-based verification "
          "before correction; a hit is a QUESTION, not a finding.")


if __name__ == "__main__":
    main()
