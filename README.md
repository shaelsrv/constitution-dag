# constitution-dag

**Map how your constitution reaches your street.**

This is an open dataset + toolkit for building a *constitutional genealogy* of any
country: a directed graph from the constitution at the top — through amendments,
statutes, and court decisions — into the offices they create and empower, across
the overlapping administrative divisions those offices serve, down to a single
place where a citizen stands.

It answers questions a citizen can act on:

- **How many distinct constitutional paths** reach my town, and through which doors
  (municipal, electoral, district, state)?
- **Where do paths meet** — the junctions and chokepoints of power — and in what
  context (which article, which section, which scope)?
- **Who governs one object** — a road, a plate of food — aspect by aspect, under
  which Act?
- **What rights do I actually hold** here — fundamental, statutory, demoted, or
  simply *absent*?
- **Who checks each office** — the feedback loops the constitution wires: impeach,
  review, audit, no-confidence?

The first dump covers **India**, pivoted on **Kotdwar, Uttarakhand** (a real
mid-size city): 29 instruments, 50 grants, 27 control edges, 12 rights, and the
full office graph context (1,100+ offices, 110 places). Every office serving
Kotdwar traces to the Constitution — 44/44, across 200+ distinct paths.

> This structure will always be incomplete. That is the point of this repo:
> nobody knows a country's real wiring better than the people inside it — the
> forest officer who knows the Forest Act, the teacher who knows the education
> code, the clerk who knows which form actually moves. This project exists so
> that knowledge can be contributed, attributed, verified, and shared.

## Quickstart (no database needed)

```bash
git clone https://github.com/shaelsrv/constitution-dag
cd constitution-dag

# how does the Constitution of India reach Kotdwar?
python dag.py dumps/india-0.10.0 paths kotdwar

# one plate of food, five jurisdictions
python dag.py dumps/india-0.10.0 object food

# what can a citizen invoke — and what does NOT exist
python dag.py dumps/india-0.10.0 rights

# HOW does an office reach you: directly, or through command chains?
python dag.py dumps/india-0.10.0 effect kotdwar "prime minister"

# INSIDE an office: the ladder from the head down to the peon
python dag.py dumps/india-0.10.0 inside "district collector"

# HOW do I get something done: the step-by-step process, officer by officer
python dag.py dumps/india-0.10.0 task            # list tasks
python dag.py dumps/india-0.10.0 task land-mutation

# export a mermaid diagram
python dag.py dumps/india-0.10.0 paths kotdwar --mermaid kotdwar.md
```

`dag.py` is stdlib-only Python 3.10+. The dumps are plain JSONL — load them into
pandas, DuckDB, Neo4j, or anything else.

## The 3D navigable map

```bash
python -m http.server 8000   # from the repo root
# open http://localhost:8000/viewer3d.html
```

`viewer3d.html` renders any dump as a flyable 3D graph: **Constitution at the
top, the place at the bottom** (altitude = layer: instruments → amendments →
statutes → national/state/district/local offices → divisions → place), free
orbit in between. Click any node for its full wiring; search flies you to an
office.

- **The hypergraph** shows two ways: the overlapping divisions render as
  distinct colored funnels into the place (each funnel is one "door"), and the
  **object lens** dropdown lights up a hyperedge — pick *food* or *roads* and
  the offices+grants carrying that scope stay lit while everything else dims.
  Objects stay non-nodes here too; a lens is a highlighted subset, exactly like
  the schema.
- **Feedback loops** are the red curved edges with particles flowing
  controller → controlled (impeach, review, audit, no-confidence). Reciprocal
  checks (President ⇄ Speaker) braid with opposite curvature so closed loops
  read at a glance. Toggle them off to see pure power-granting flow.

Uses three.js + 3d-force-graph from a CDN; for offline/self-host use, download
those two files beside the page and repoint the script tags.

## Build your own country's map

Start from [AGENTS.md](AGENTS.md). The short version:

1. **Seed** (a weekend, one person + an LLM assistant): ~12 apex offices, your
   constitution + its landmark amendments as instrument rows, the famous control
   loops (who impeaches whom, who audits whom), and ONE local chain from your own
   town up. That alone yields a working paths/objects/rights report.
2. **Nurture**: run scans (`dag.py paths <your-town>` shows ungrounded offices —
   that list IS your to-do list), fix inaccuracies against primary sources, add
   scoped edges for the objects you care about, record the rights ledger.
3. **Version**: publish your dump as `dumps/<country>-<semver>/` with a manifest
   and SHA256SUMS. Better data replaces worse data, and the version history keeps
   every prior state citable.

## Versioned dumps

| dump | contents | source |
|---|---|---|
| `dumps/india-0.10.0` | **current** — 14 citizen task flows (grown by a generate->answer->review enrichment loop) | [nationAtlas](https://emergencemachine.com) (private during beta) |
| `dumps/india-0.9.0` | task flows: how to get 6 real things done (mutation, certificate, permit, ration, RTE, MGNREGA) step by step | [nationAtlas](https://emergencemachine.com) (private during beta) |
| `dumps/india-0.8.0` | internal feedback loops: 10k+ checks inside offices (who audits/verifies/inspects whom) | [nationAtlas](https://emergencemachine.com) (private during beta) |
| `dumps/india-0.7.0` | full internal office structure: 278k sanctioned posts (DM to peon) across 6 office classes | [nationAtlas](https://emergencemachine.com) (private during beta) |
| `dumps/india-0.6.0` | internal office structure: 2,569 post-types (DM down to peon) with reporting ladders | [nationAtlas](https://emergencemachine.com) (private during beta) |
| `dumps/india-0.5.0` | the grounding invariant: 1,178/1,178 offices reach the Constitution (0 ungrounded); strict-clean | [nationAtlas](https://emergencemachine.com) (private during beta) |
| `dumps/india-0.4.0` | coverage pass: 625 template-grounded offices + 7 national regulators; backlog 96%→42% | [nationAtlas](https://emergencemachine.com) (private during beta) |
| `dumps/india-0.3.0` | Emergency + Panchayat parts; loop completeness 0.974, one honest gap | [nationAtlas](https://emergencemachine.com) (private during beta) |
| `dumps/india-0.2.0` | constitutional-completeness pass (all 24 domains allocated; 9 constitutional bodies added) | [nationAtlas](https://emergencemachine.com) (private during beta) |
| `dumps/india-0.1.1` | India pilot: genealogy layer + Kotdwar-grounded office graph | [nationAtlas](https://emergencemachine.com) (private during beta) |
| `dumps/india-0.1.0` | superseded (integrity bug caught by validate.py — see CHANGELOG) | — |

Dumps mirror to Kaggle for data-science use — see `kaggle/`. Format spec in
[SCHEMA.md](SCHEMA.md). Every dump directory carries `manifest.json` (version,
counts, license) and `SHA256SUMS`; releases are tagged and signed.

## The honesty rules (non-negotiable)

These are inherited from the parent project's observational discipline and are
what make the data trustworthy enough to merge:

1. **Provenance on every row** — `source` + `confidence` (`high|medium|low`).
   `high` is *earned* by verification against the primary legal text, never
   self-declared. Act-level attributions you haven't checked to the section are
   `medium`, and that's fine — labeled uncertainty is data, hidden uncertainty
   is contamination.
2. **Model votes are not a source.** We tested this: two grounded LLM verifiers
   refuted a true municipal fact and confirmed two mutually exclusive claims.
   LLMs are excellent *proposers* and terrible *authorities*. Verification means
   retrieving the provision or an authoritative record and citing it.
3. **Objects never enter the schema.** A road, food, a school building — these
   are families of `scope`-tagged edges ("roads: land acquisition"), not nodes.
   This is what keeps the model extensible without schema churn.
4. **Checks are not grants.** Control edges (impeach/review/audit) are a separate
   overlay from power-granting edges; path counts stay meaningful because the
   two are never mixed.
5. **Absence is data.** A right that does not exist (`kind='absent'`) or a power
   that was removed (a `constrained_by` edge from an amendment) is recorded as
   deliberately as any grant.

## Contributing

Quality is enforced in layers — CI validation, provenance gates, adversarial scans, scoped authorities, versioned accountability: see [QUALITY.md](QUALITY.md). Then see [CONTRIBUTING.md](CONTRIBUTING.md) — including how domain experts (the
forest-department case) contribute what they know, how attribution works, and
the signing scheme that lets downstream users verify who vouched for what.

## License

Code: [MIT](LICENSE). Data (`dumps/`): [CC-BY 4.0](DATA_LICENSE) — use it for
anything, attribute the contributors.
