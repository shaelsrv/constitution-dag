#!/usr/bin/env python3
"""constitution-dag dump validator — the mechanical quality gate.

Everything here BLOCKS a merge (exit 1). It enforces the parts of the honesty
rules a machine can check; CONTRIBUTING.md covers the parts it cannot.

  structure     required fields per table; enum vocabularies; JSONL well-formed
  integrity     every foreign id resolves inside the dump; UNIQUE keys hold
  provenance    every genealogy row carries source + confidence; provision
                present on grants; confidence='high' requires a non-empty source
  honesty       absence-is-data (kind='absent' rows must have NO instrument);
                object scopes follow "<object>: <aspect>" so object views work;
                deprecated rows keep their reason
  checksums     SHA256SUMS matches file bytes; manifest counts match reality

Usage:  python validate.py dumps/india-0.1.0 [--strict]
--strict additionally fails on warnings (release mode; PR mode warns only).
"""

import hashlib
import json
import os
import re
import sys

ENUMS = {
    "legal_instruments.kind": {"constitution", "amendment", "statute",
                               "state_constitution", "charter", "order",
                               "court_decision", "convention"},
    "instrument_edges.relation": {"created_by", "empowered_by", "constrained_by",
                                  "abolished_by"},
    "constitutional_controls.mechanism": {"appoint", "remove", "impeach", "veto",
                                          "assent", "audit", "review", "supervise",
                                          "dissolve", "no_confidence"},
    "citizen_rights.kind": {"fundamental", "statutory", "legal", "absent"},
    "confidence": {"high", "medium", "low"},
}
GENEALOGY = ("legal_instruments", "instrument_edges", "constitutional_controls",
             "division_kind_grants", "domain_allocations", "citizen_rights")
REQUIRED = {
    "legal_instruments": ("nation_id", "kind", "title", "citation"),
    "instrument_edges": ("instrument_id", "position_id", "relation", "provision"),
    "constitutional_controls": ("controller_id", "controlled_id", "mechanism"),
    "division_kind_grants": ("nation_id", "division_kind", "instrument_id",
                             "provision"),
    "domain_allocations": ("nation_id", "domain", "level", "instrument_id",
                           "provision"),
    "citizen_rights": ("nation_id", "right_name", "kind"),
}
UNIQUE = {
    "legal_instruments": ("nation_id", "citation"),
    "instrument_edges": ("instrument_id", "position_id", "relation", "provision"),
    "constitutional_controls": ("controller_id", "controlled_id", "mechanism"),
    "division_kind_grants": ("nation_id", "division_kind", "instrument_id",
                             "provision"),
    "domain_allocations": ("nation_id", "domain", "level", "provision"),
    "citizen_rights": ("nation_id", "right_name"),
}
SCOPE_RE = re.compile(r"^[a-z_]+ ?: .+")   # "<object>: <aspect …>"

errors, warnings = [], []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


ROLE_SPEC_ENUMS = {
    "status": {"active", "vacant", "retired", "merged", "split", "abolished", "planned"},
    "role_type": {"elected", "appointed", "employee", "contractor", "ai_agent",
                  "robot", "hybrid"},
    "performed_type": {"human", "ai", "robot", "hybrid"},
    "automation": {"human_only", "human_in_the_loop", "supervised_autonomy",
                   "full_autonomy"},
    "capability": {"physical_inspection", "financial_approval", "policy_analysis",
                   "investigation", "procurement", "public_communication",
                   "legal_review", "compliance", "record_keeping",
                   "emergency_response", "service_delivery", "supervision",
                   "administration"},
}
ROLE_SPEC_REQUIRED = ["role_id", "dump_version", "revision_id", "name",
                      "organization_id", "status", "role_type", "purpose",
                      "responsibility_ids", "performed_by", "capabilities",
                      "effective_from", "source_ids", "confidence"]


def validate_role_spec(specdir):
    """Enforce the Core v1 contract on a role_spec/<version> directory."""
    def jl(name):
        p = os.path.join(specdir, name + ".jsonl")
        if not os.path.exists(p):
            return []
        with open(p, encoding="utf-8") as f:
            return [json.loads(x) for x in f if x.strip()]

    roles = jl("roles")
    if not roles:
        err(f"role-spec: no roles.jsonl in {specdir}")
        return
    mpath = os.path.join(specdir, "manifest.json")
    if os.path.exists(mpath):
        m = json.load(open(mpath, encoding="utf-8"))
        if m.get("format") != "role-spec/core-v1":
            err(f"role-spec: manifest format is {m.get('format')!r}, "
                "expected 'role-spec/core-v1'")
    else:
        err("role-spec: manifest.json missing")

    resp_ids = {r["resp_id"] for r in jl("responsibilities")}
    auth_ids = {a["auth_id"] for a in jl("authorities")}
    ctrl_ids = {c["ctrl_id"] for c in jl("controls")}
    src_ids = {s["src_id"] for s in jl("sources")}
    cap_ids = {c["cap_id"] for c in jl("capabilities")}
    org_ids = {o["organization_id"] for o in jl("organizations")}
    role_ids = set()

    def ref(role_i, field, values, universe, label):
        for v in (values or []):
            if v not in universe:
                err(f"role-spec roles[{role_i}] {field} {v!r} not in {label}")

    for i, r in enumerate(roles):
        for f in ROLE_SPEC_REQUIRED:
            if r.get(f) in (None, ""):
                err(f"role-spec roles[{i}] missing required field {f}")
        rid = r.get("role_id")
        if rid in role_ids:
            err(f"role-spec roles[{i}] duplicate role_id {rid!r}")
        role_ids.add(rid)
        if r.get("status") not in ROLE_SPEC_ENUMS["status"]:
            err(f"role-spec roles[{i}] bad status {r.get('status')!r}")
        if r.get("role_type") not in ROLE_SPEC_ENUMS["role_type"]:
            err(f"role-spec roles[{i}] bad role_type {r.get('role_type')!r}")
        pb = r.get("performed_by") or {}
        if pb.get("type") not in ROLE_SPEC_ENUMS["performed_type"]:
            err(f"role-spec roles[{i}] bad performed_by.type {pb.get('type')!r}")
        if pb.get("automation") not in ROLE_SPEC_ENUMS["automation"]:
            err(f"role-spec roles[{i}] bad performed_by.automation {pb.get('automation')!r}")
        c = r.get("confidence")
        if not isinstance(c, (int, float)) or not (0 <= c <= 1):
            err(f"role-spec roles[{i}] confidence {c!r} not a float in [0,1]")
        if r.get("organization_id") not in org_ids:
            err(f"role-spec roles[{i}] organization_id {r.get('organization_id')!r} "
                "not in organizations.jsonl")
        for cap in (r.get("capabilities") or []):
            if not cap.startswith("CAP-") or cap[4:] not in ROLE_SPEC_ENUMS["capability"]:
                err(f"role-spec roles[{i}] capability {cap!r} not in vocabulary")
            if cap not in cap_ids:
                err(f"role-spec roles[{i}] capability {cap!r} not in capabilities.jsonl")
        if not (r.get("source_ids") or []) and (r.get("confidence") or 0) > 0.3:
            err(f"role-spec roles[{i}] has no source_ids but confidence>{0.3} — "
                "an unsourced claim must declare confidence<=low")
        ref(i, "responsibility_ids", r.get("responsibility_ids"), resp_ids, "responsibilities")
        ref(i, "authority_ids", r.get("authority_ids"), auth_ids, "authorities")
        ref(i, "control_ids", r.get("control_ids"), ctrl_ids, "controls")
        ref(i, "source_ids", r.get("source_ids"), src_ids, "sources")
    # controls point back at real roles
    for i, c in enumerate(jl("controls")):
        by = c.get("exercised_by_role_id")
        if by and by not in role_ids:
            warn(f"role-spec controls[{i}] exercised_by_role_id {by!r} not a role in this export")


def load(dumpdir):
    d = {}
    for name in sorted(os.listdir(dumpdir)):
        if not name.endswith(".jsonl"):
            continue
        rows = []
        with open(os.path.join(dumpdir, name), encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as e:
                    err(f"{name}:{i} malformed JSON: {e}")
        d[name[:-6]] = rows
    return d


def main():
    dumpdir = sys.argv[1]
    strict = "--strict" in sys.argv
    d = load(dumpdir)

    # ── checksums + manifest ──
    try:
        manifest = json.load(open(os.path.join(dumpdir, "manifest.json"),
                                  encoding="utf-8"))
    except OSError:
        err("manifest.json missing")
        manifest = {}
    sums_path = os.path.join(dumpdir, "SHA256SUMS")
    if os.path.exists(sums_path):
        for line in open(sums_path, encoding="utf-8"):
            if not line.strip():
                continue
            want, fname = line.split(None, 1)
            fname = fname.strip()
            p = os.path.join(dumpdir, fname)
            if not os.path.exists(p):
                err(f"SHA256SUMS lists missing file {fname}")
                continue
            got = hashlib.sha256(open(p, "rb").read()).hexdigest()
            if got != want:
                err(f"checksum mismatch: {fname}")
    else:
        err("SHA256SUMS missing")
    for t, n in (manifest.get("counts") or {}).items():
        if t in d and len(d[t]) != n:
            err(f"manifest count for {t} is {n} but file has {len(d[t])}")

    # ── id sets for integrity ──
    ids = {t: {r["id"] for r in d.get(t, []) if "id" in r}
           for t in ("legal_instruments", "positions", "divisions", "places",
                     "nations", "jurisdictions")}
    pos_slugs = {r["slug"] for r in d.get("positions", [])}

    def check_fk(table, field, target, nullable=True):
        for i, r in enumerate(d.get(table, [])):
            v = r.get(field)
            if v is None:
                if not nullable:
                    err(f"{table}[{i}] {field} is null")
                continue
            if v not in ids[target]:
                err(f"{table}[{i}] {field}={v} does not resolve in {target}")

    check_fk("instrument_edges", "instrument_id", "legal_instruments", False)
    check_fk("instrument_edges", "position_id", "positions", False)
    check_fk("constitutional_controls", "controller_id", "positions", False)
    check_fk("constitutional_controls", "controlled_id", "positions", False)
    check_fk("constitutional_controls", "instrument_id", "legal_instruments")
    check_fk("division_kind_grants", "instrument_id", "legal_instruments", False)
    check_fk("domain_allocations", "instrument_id", "legal_instruments", False)
    check_fk("citizen_rights", "instrument_id", "legal_instruments")
    check_fk("legal_instruments", "amends_id", "legal_instruments")
    check_fk("position_divisions", "position_id", "positions", False)
    check_fk("position_divisions", "division_id", "divisions", False)
    check_fk("place_divisions", "place_id", "places", False)
    check_fk("place_divisions", "division_id", "divisions", False)
    check_fk("office_posts", "position_id", "positions", False)
    check_fk("office_posts", "instrument_id", "legal_instruments")
    # office_posts: every post needs provenance (internal-structure integrity);
    # post_reports must reference posts that exist in the dump (checked below)
    seen_stable = {}
    for i, p in enumerate(d.get("office_posts", [])):
        if p.get("post_name") in (None, ""):
            err(f"office_posts[{i}] missing post_name")
        sid = p.get("stable_id")
        if not sid:
            err(f"office_posts[{i}] missing stable_id (external reference)")
        elif sid in seen_stable:
            err(f"office_posts[{i}] duplicate stable_id {sid!r}")
        else:
            seen_stable[sid] = i
        if p.get("confidence") not in ENUMS["confidence"]:
            err(f"office_posts[{i}] bad confidence {p.get('confidence')!r}")
        if not (p.get("source") or "").strip():
            warn(f"office_posts[{i}] post '{p.get('post_name')}' has no source")
    # post_reports must reference posts that exist in the dump
    post_ids = {p["id"] for p in d.get("office_posts", []) if "id" in p}
    for i, r in enumerate(d.get("post_reports", [])):
        for f in ("subordinate_id", "superior_id"):
            if r.get(f) not in post_ids:
                err(f"post_reports[{i}] {f}={r.get(f)} not an office_post in the dump")
    for i, r in enumerate(d.get("post_controls", [])):
        for f in ("controller_id", "controlled_id"):
            if r.get(f) not in post_ids:
                err(f"post_controls[{i}] {f}={r.get(f)} not an office_post in the dump")
        if not (r.get("mechanism") or "").strip():
            err(f"post_controls[{i}] missing mechanism")

    # ── per-table structure / enums / provenance / uniqueness ──
    for t in GENEALOGY:
        seen = set()
        for i, r in enumerate(d.get(t, [])):
            for f in REQUIRED[t]:
                if r.get(f) in (None, ""):
                    err(f"{t}[{i}] missing required field {f}")
            conf = r.get("confidence")
            if conf not in ENUMS["confidence"]:
                err(f"{t}[{i}] confidence={conf!r} not in high|medium|low")
            if conf == "high" and not (r.get("source") or "").strip():
                err(f"{t}[{i}] confidence=high without a source — high is EARNED")
            if not (r.get("source") or "").strip():
                warn(f"{t}[{i}] has no source")
            key_fields = UNIQUE[t]
            key = tuple(r.get(k) for k in key_fields)
            if key in seen:
                err(f"{t}[{i}] duplicate key {dict(zip(key_fields, key))}")
            seen.add(key)
            for enum_key, allowed in ENUMS.items():
                et, _, ef = enum_key.partition(".")
                if et == t and ef and r.get(ef) not in allowed:
                    err(f"{t}[{i}] {ef}={r.get(ef)!r} not in {sorted(allowed)}")

    # ── honesty rules ──
    for i, r in enumerate(d.get("citizen_rights", [])):
        if r.get("kind") == "absent" and r.get("instrument_id") is not None:
            err(f"citizen_rights[{i}] kind=absent must have NO instrument — "
                "the absence IS the fact")
        if r.get("kind") != "absent" and r.get("instrument_id") is None:
            warn(f"citizen_rights[{i}] '{r.get('right_name')}' has no instrument")
        g = r.get("guarantor_slug")
        if g and g not in pos_slugs:
            warn(f"citizen_rights[{i}] guarantor_slug '{g}' not in dump positions")
    for i, r in enumerate(d.get("instrument_edges", [])):
        s = r.get("scope")
        if s and ":" in s[:24] and not SCOPE_RE.match(s):
            warn(f"instrument_edges[{i}] scope {s!r} deviates from "
                 "'<object>: <aspect>' convention")
    for i, r in enumerate(d.get("positions", [])):
        if r.get("deprecated_at") and not (r.get("deprecated_reason") or "").strip():
            err(f"positions[{i}] deprecated without a reason — retraction needs "
                "a stated cause")

    # ── grounding invariant: every live office reaches the Constitution ──
    # (warning in PR mode; --strict release mode makes it blocking)
    granted_pos = {r["position_id"] for r in d.get("instrument_edges", [])
                   if r.get("relation") in ("created_by", "empowered_by")}
    ungrounded = [p for p in d.get("positions", [])
                  if not p.get("deprecated_at") and p["id"] not in granted_pos]
    if ungrounded:
        warn(f"grounding invariant: {len(ungrounded)} live office(s) have no "
             "created_by/empowered_by instrument edge — every role must reach "
             "the constitution through SOME channel (see AGENTS.md; channel "
             "grounding at medium confidence is the honest minimum)")

    # ── constitution root exists per nation with genealogy rows ──
    roots = {r["nation_id"] for r in d.get("legal_instruments", [])
             if r.get("kind") in ("constitution", "convention")}
    for nid in {r["nation_id"] for r in d.get("legal_instruments", [])}:
        if nid not in roots:
            err(f"nation_id={nid} has instruments but no constitution/convention root")

    # ── Universal Role Schema (Core v1) validation, when a role_spec dir is given ──
    specdir = None
    if "--role-spec" in sys.argv:
        specdir = sys.argv[sys.argv.index("--role-spec") + 1]
    else:
        sib = os.path.join(os.path.dirname(dumpdir.rstrip("/\\")) or ".",
                           "..", "role_spec", os.path.basename(dumpdir.rstrip("/\\")))
        if os.path.isdir(sib):
            specdir = sib
    if specdir and os.path.isdir(specdir):
        validate_role_spec(specdir)

    print(f"validate: {len(errors)} error(s), {len(warnings)} warning(s)")
    for e in errors:
        print("  ERROR  " + e)
    shown = warnings if strict else warnings[:20]
    for w in shown:
        print("  warn   " + w)
    if not strict and len(warnings) > 20:
        print(f"  … {len(warnings) - 20} more warnings")
    sys.exit(1 if errors or (strict and warnings) else 0)


if __name__ == "__main__":
    main()
