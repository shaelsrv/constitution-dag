#!/usr/bin/env python3
"""constitution-dag: portable analyzer over a versioned dump. Stdlib only.

Load a dump directory (JSONL files + manifest.json) and answer:
  * how many constitutional paths reach a place, and where they meet
  * which offices have NO known constitutional path (your grounding gap)
  * the OBJECT view: one physical thing (roads, food) split across offices by aspect
  * the RIGHTS view: what a citizen can invoke, cannot invoke, or holds demoted

Usage:
  python dag.py dumps/india-0.1.0 paths kotdwar
  python dag.py dumps/india-0.1.0 object food kotdwar
  python dag.py dumps/india-0.1.0 rights
  python dag.py dumps/india-0.1.0 paths kotdwar --mermaid out.md
"""

import json
import os
import sys
from collections import defaultdict

MAX_PATHS, CUTOFF = 400, 9
GENERIC_COMPETENCE = "Art. 245-246 + Seventh Schedule (legislative competence)"


def load(dumpdir):
    d = {}
    for name in os.listdir(dumpdir):
        if name.endswith(".jsonl"):
            with open(os.path.join(dumpdir, name), encoding="utf-8") as f:
                d[name[:-6]] = [json.loads(line) for line in f if line.strip()]
    with open(os.path.join(dumpdir, "manifest.json"), encoding="utf-8") as f:
        d["_manifest"] = json.load(f)
    return d


# ── graph construction (mirrors nationAtlas app/constitution_dag.py) ─────────

def build(d, place_slug):
    place = next((p for p in d["places"] if p["slug"] == place_slug), None)
    if not place:
        raise SystemExit(f"unknown place: {place_slug} "
                         f"(have: {', '.join(sorted(p['slug'] for p in d['places'])[:20])} …)")
    nodes, edges = {}, defaultdict(list)          # node -> attrs; src -> [(dst, etype, ctx)]

    def add(n, **attrs):
        nodes.setdefault(n, attrs)

    def link(a, b, etype, ctx=""):
        edges[a].append((b, etype, ctx))

    pn = f"place:{place_slug}"
    add(pn, layer="place", label=place["name"])
    div_ids = {r["division_id"] for r in d["place_divisions"]
               if r["place_id"] == place["id"]}
    divs = {v["id"]: v for v in d["divisions"] if v["id"] in div_ids}
    for v in divs.values():
        add(f"div:{v['id']}", layer="division", label=v["name"], kind=v["kind"])
        link(f"div:{v['id']}", pn, "covers", v["kind"])

    pos_by_id = {p["id"]: p for p in d["positions"] if not p.get("deprecated_at")}
    serving = {}
    for r in d["position_divisions"]:
        if r["division_id"] in div_ids and r["position_id"] in pos_by_id:
            serving.setdefault(r["position_id"], set()).add(r["division_id"])
    for pid, dvs in serving.items():
        p = pos_by_id[pid]
        add(f"pos:{p['slug']}", layer="office", label=p["name"], branch=p["branch"])
        for dv in dvs:
            link(f"pos:{p['slug']}", f"div:{dv}", "serves")

    doms = defaultdict(list)
    for r in d["position_domains"]:
        doms[r["position_id"]].append(r["domain"])

    instr = {i["id"]: i for i in d["legal_instruments"]}
    used = set()
    for e in d["instrument_edges"]:
        if e["relation"] in ("created_by", "empowered_by") and e["position_id"] in serving:
            i = instr.get(e["instrument_id"])
            if not i:
                continue
            used.add(i["id"])
            a = i.get("amends_id")
            while a and a in instr and a not in used:
                used.add(a)
                a = instr[a].get("amends_id")
            p = pos_by_id[e["position_id"]]
            ctx = e["provision"] + ((" | " + e["scope"]) if e.get("scope") else "")
            link(f"instr:{i['id']}", f"pos:{p['slug']}", e["relation"], ctx)
    root = None
    for iid in used:
        i = instr[iid]
        add(f"instr:{iid}", layer="instrument", label=i["title"], kind=i["kind"])
        if i["kind"] == "constitution":
            root = f"instr:{iid}"
        if i.get("amends_id") in used:
            link(f"instr:{i['amends_id']}", f"instr:{iid}", "amended_by", i["citation"])
    alloc = {a["domain"]: a["provision"] for a in d["domain_allocations"]}
    if root:
        for iid in used:
            i = instr[iid]
            if f"instr:{iid}" == root or i.get("amends_id"):
                continue
            if i["kind"] in ("statute", "order", "charter"):
                granted = {e["position_id"] for e in d["instrument_edges"]
                           if e["instrument_id"] == iid}
                ds = {x for pid in granted for x in doms.get(pid, [])}
                ctx = next((alloc[x] for x in sorted(ds) if x in alloc),
                           GENERIC_COMPETENCE)
                link(root, f"instr:{iid}", "competence", ctx)
    for r in d["dependencies"]:
        if r["provider_id"] in serving and r["dependent_id"] in serving \
                and r["provider_id"] != r["dependent_id"]:
            link(f"pos:{pos_by_id[r['provider_id']]['slug']}",
                 f"pos:{pos_by_id[r['dependent_id']]['slug']}",
                 "depends", r["dep_type"])
    return nodes, dict(edges), root, pn


def simple_paths(edges, src, dst, cutoff=CUTOFF, cap=MAX_PATHS):
    out, stack = [], [(src, [src])]
    while stack and len(out) < cap:
        node, path = stack.pop()
        if node == dst:
            out.append(path)
            continue
        if len(path) > cutoff:
            continue
        for nxt, _, _ in edges.get(node, []):
            if nxt not in path:
                stack.append((nxt, path + [nxt]))
    return out, (len(out) >= cap)


def edge_attr(edges, a, b):
    for dst, etype, ctx in edges.get(a, []):
        if dst == b:
            return etype, ctx
    return "", ""


def paths_report(d, place_slug, mermaid_out=None):
    nodes, edges, root, pn = build(d, place_slug)
    if not root:
        print("no constitution instrument in dump")
        return
    paths, truncated = simple_paths(edges, root, pn)
    on_path = {n for p in paths for n in p}
    offices = {n for n, a in nodes.items() if a["layer"] == "office"}
    print(f"CONSTITUTION -> {place_slug} : {len(paths)} distinct paths"
          + (" (truncated)" if truncated else ""))
    print(f"  offices grounded {len(offices & on_path)} / {len(offices)}")
    for n in sorted(offices - on_path):
        print(f"    no known constitutional path: {nodes[n]['label']}")
    inbound = defaultdict(set)
    for p in paths:
        for a, b in zip(p, p[1:]):
            inbound[b].add(a)
    print("\n  WHERE PATHS MEET:")
    for n, preds in sorted(inbound.items(), key=lambda kv: -len(kv[1])):
        if len(preds) < 2:
            continue
        print(f"   [{nodes[n]['layer']:10s}] {nodes[n]['label']} <- {len(preds)} routes")
        for a in sorted(preds):
            et, ctx = edge_attr(edges, a, n)
            print(f"        via {nodes[a]['label']} ({et}{': ' + ctx if ctx else ''})")
    if mermaid_out:
        write_mermaid(nodes, edges, paths, mermaid_out)
        print(f"\nmermaid written: {mermaid_out}")


def write_mermaid(nodes, edges, paths, out):
    ids, lines, seen = {}, ["flowchart TD"], set()

    def nid(n):
        return ids.setdefault(n, f"n{len(ids)}")

    for p in paths:
        for a, b in zip(p, p[1:]):
            if (a, b) in seen:
                continue
            seen.add((a, b))
            for n in (a, b):
                if nid(n) not in [l.split("[")[0].strip() for l in lines]:
                    pass
            et, ctx = edge_attr(edges, a, b)
            la = nodes[a]["label"].replace('"', "'")
            lb = nodes[b]["label"].replace('"', "'")
            lines.append(f'  {nid(a)}["{la}"] -- "{et}" --> {nid(b)}["{lb}"]')
    with open(out, "w", encoding="utf-8") as f:
        f.write("```mermaid\n" + "\n".join(lines) + "\n```\n")


def object_report(d, prefix, place_slug=None):
    pos_by_id = {p["id"]: p for p in d["positions"]}
    instr = {i["id"]: i for i in d["legal_instruments"]}
    print(f"OBJECT '{prefix}' — aspects and their masters:")
    for e in d["instrument_edges"]:
        if (e.get("scope") or "").startswith(prefix + ":"):
            p, i = pos_by_id.get(e["position_id"]), instr.get(e["instrument_id"])
            if p and i:
                print(f"  {e['scope']}")
                print(f"      -> {p['name']} ({p['level']})")
                print(f"         per {i['citation']} [{e['provision']}] "
                      f"conf={e['confidence']}")


def rights_report(d):
    instr = {i["id"]: i for i in d["legal_instruments"]}
    order = {"fundamental": 0, "statutory": 1, "legal": 2, "absent": 3}
    for r in sorted(d["citizen_rights"], key=lambda x: (order.get(x["kind"], 9),
                                                        x["right_name"])):
        i = instr.get(r.get("instrument_id"))
        print(f"\n[{r['kind'].upper():11s}] {r['right_name']}")
        if i:
            print(f"    per {i['citation']} [{r.get('provision') or ''}]")
        for k, lab in (("scope", "applies to"), ("limitation", "but"),
                       ("note", "note")):
            if r.get(k):
                print(f"    {lab}: {r[k]}")
        if r.get("guarantor_slug"):
            g = next((p for p in d["positions"]
                      if p["slug"] == r["guarantor_slug"]), None)
            if g:
                print(f"    invoke before: {g['name']} ({g['level']})")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    d = load(sys.argv[1])
    cmd = sys.argv[2]
    if cmd == "paths":
        out = None
        if "--mermaid" in sys.argv:
            out = sys.argv[sys.argv.index("--mermaid") + 1]
        paths_report(d, sys.argv[3], out)
    elif cmd == "object":
        object_report(d, sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
    elif cmd == "rights":
        rights_report(d)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
