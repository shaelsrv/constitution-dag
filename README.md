# constitution-dag

**The GPS of accountability.**

Public officials should be judged by more than speeches, slogans, and campaign
advertisements. They should be judged by the **actions they took while holding
public responsibility**.

This is an open, navigable, source-backed map of a government — from the
constitution at the top, through the amendments, statutes, and court decisions
that create and empower every office, across the overlapping divisions those
offices serve, down to the single place where a citizen stands.

That structural map is what ships **today**. The map is the substrate for the
larger goal: a record of real public **actions**, each anchored to the exact role
and authority behind it, so that for any action a citizen can see —

- **Who** made the decision
- **Which public role** gave them the authority
- **What evidence** supports the record
- **How much public money** was involved
- **What controls and approvals** applied
- **What happened afterward**
- **How the public** assessed it

Support an action. Oppose it. Explain why. Then, when the time for accountability
comes, citizens can review the complete record and decide with more than a slogan
to go on. Every citizen evaluates public actions **according to their own values** —
the record is neutral; the judgment is yours.

And because governments change — and because public work is beginning to move
between people, AI agents, and robots — the map keeps a **visible change history**:
you can see exactly what changed, where the responsibility went, and what controls
remain. Government should not feel like a black box.

> **Status, honestly.** What exists now: the full structural map (offices,
> authorities, controls, rights, internal posts, task flows) with provenance on
> every row, plus a timeline of structural **events** with their actors and legal
> instruments. The per-action money, outcome, and public-assessment fields are the
> roadmap, not yet in the dump — this README marks that line rather than blur it,
> because [the honesty rules](#the-honesty-rules-non-negotiable) are the point.

## What it answers

Under the accountability layer sits a complete structural map. It answers questions
a citizen can act on:

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
- **What are the roles INSIDE an office** — from the District Magistrate down to
  the Lekhpal who holds your land record and the peon who moves the file — with
  each post's decision power and its internal feedback loops (who audits/verifies/
  inspects whom)?
- **How do I actually get something done** — the ordered step-by-step process for a
  real task (land mutation, ration card, FIR, pension…): which officer does what,
  who approves, the statutory time limit, and where to appeal if stuck?

It also **exports a universal, organization-agnostic role format** — the
[Universal Role Schema (Core v1)](ROLE_SPEC.md). Every office and internal post
projects into a small stable record (`role_id`, `purpose`, `responsibility_ids`,
`performed_by`, a shared **capability profile**, `confidence`, `source_ids`), so a
government's wiring becomes queryable in the *same* shape a company, NGO, or future
AI organization would export — enabling cross-organization questions like *"every
role that can approve a payment"* or *"every role suitable for automation."*

The pilot covers **India**, pivoted on **Kotdwar, Uttarakhand**. Every office
serving Kotdwar traces to the Constitution. Latest dump (`india-0.12.0`) holds:
the genealogy layer (instruments → grants → offices → divisions → place, with the
control web, rights ledger, and Seventh-Schedule domain allocations), the full
**internal office structure** (~278k sanctioned post-types, DM to peon, across 6
office classes), **10k+ internal feedback loops**, and **82 citizen task flows**
(and growing) — every role carrying a **stable external ID** so it can be
referenced from outside the dump, and a companion **Universal Role Schema**
export (`role_spec/india-0.12.0/`). Layers grow version by version; see the table
below and CHANGELOG.md.

## Why this exists

Most government information is *technically* public. That doesn't mean it's
understandable.

> Budgets live in PDFs. Departments have separate websites. Responsibilities
> overlap. Finding a straight answer takes hours.

We're building an open, navigable knowledge graph that connects it all — so you
can explore your country, follow public spending, understand institutions, and
contribute verified information back. Citizens deserve to understand the systems
they fund. **Better maps make better accountability.**

This structure will always be incomplete, and that is the whole point: nobody
knows a country's real wiring better than the people inside it — the forest
officer who knows the Forest Act, the teacher who knows the education code, the
clerk who knows which form actually moves. This project exists so that knowledge
can be contributed, attributed, verified, and shared — an atlas of your nation,
created by the people who know it best.

## Quickstart (no database needed)

```bash
git clone https://github.com/shaelsrv/constitution-dag
cd constitution-dag

# how does the Constitution of India reach Kotdwar?
python dag.py dumps/india-0.12.0 paths kotdwar

# one plate of food, five jurisdictions
python dag.py dumps/india-0.12.0 object food

# what can a citizen invoke — and what does NOT exist
python dag.py dumps/india-0.12.0 rights

# HOW does an office reach you: directly, or through command chains?
python dag.py dumps/india-0.12.0 effect kotdwar "prime minister"

# INSIDE an office: the ladder from the head down to the peon
python dag.py dumps/india-0.12.0 inside "district collector"

# HOW do I get something done: the step-by-step process, officer by officer
python dag.py dumps/india-0.12.0 task            # list tasks
python dag.py dumps/india-0.12.0 task land-mutation

# the UNIVERSAL ROLE SCHEMA export: capability profile + linked entities
python dag.py role-spec role_spec/india-0.12.0                     # summary
python dag.py role-spec role_spec/india-0.12.0 cap:physical_inspection
python dag.py role-spec role_spec/india-0.12.0 role:tehsildar

# export a mermaid diagram
python dag.py dumps/india-0.12.0 paths kotdwar --mermaid kotdwar.md
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

0. **Scaffold** — don't start from a blank page. `python newdump.py new mycountry`
   copies a validates-green starter (`dumps/_template/`, a tiny fictional country
   that already produces a full report) into `dumps/mycountry-0.1.0/`. Edit it into
   your country; `python newdump.py stamp <dir>` refreshes the manifest + checksums.
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
| `dumps/india-0.12.0` | **current** — Universal Role Schema (Core v1) export + 82 task flows (loop round 3) | [nationAtlas](https://emergencemachine.com) (private during beta) |
| `dumps/india-0.11.0` | stable external role IDs + 46 task flows (loop round 2) | [nationAtlas](https://emergencemachine.com) (private during beta) |
| `dumps/india-0.10.0` | 14 citizen task flows (grown by a generate->answer->review enrichment loop) | [nationAtlas](https://emergencemachine.com) (private during beta) |
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

## Help build the atlas of your nation

Government shouldn't feel like a black box. Help make it navigable for everyone —
there's a role at every level of involvement:

- **Explore your country** — follow public spending, understand institutions,
  trace who answers for what.
- **Contribute code. Improve data.** — fix an inaccuracy, add a task flow, deepen
  an office's structure.
- **Add verified sources** — attach primary-source references that upgrade a claim
  from *estimated* to *earned*.
- **Review contributions** — vouch for what others submit under the signing scheme.
- **Host a server** — run an instance for your region.
- **Become a country maintainer** — own the map for a nation and shepherd its
  growth.

Quality is enforced in layers — CI validation, provenance gates, adversarial
scans, scoped authorities, versioned accountability: see [QUALITY.md](QUALITY.md).
Then see [CONTRIBUTING.md](CONTRIBUTING.md) — how domain experts (the
forest-department case) contribute what they know, how attribution works, and the
signing scheme that lets downstream users verify who vouched for what.

## License & attribution

Open and adoption-friendly by design — use it for anything, commercial or not:

- **Code / tooling:** [MIT](LICENSE).
- **Data (`dumps/`, `role_spec/`) and docs:** [CC-BY 4.0](DATA_LICENSE).

The one thing we ask (this is the CC-BY attribution): credit **constitution-dag,
part of the [Emergence Machine](https://emergencemachine.com) project**, with a
link back to this repo. That upstream credit is the whole reason it's openly
licensed — it's how the work gets found and built on. Individual contributors are
credited in `ATTRIBUTIONS.jsonl`; see [`NOTICE`](NOTICE) for the full guidance and
[`CITATION.cff`](CITATION.cff) for a machine-readable citation (GitHub's "Cite this
repository" button).
