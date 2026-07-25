# Dump format: `constitution-dag-dump/1`

A dump is a directory of JSONL files (one row per line) + `manifest.json` +
`SHA256SUMS`. All ids are integers local to the dump; join on them freely.
Every substantive table carries `source` (free text citing where the fact came
from) and `confidence` (`high|medium|low` — see the honesty rules in README).

## Core genealogy tables

### legal_instruments
The legal texts. `kind`: `constitution | amendment | statute | state_constitution
| charter | order | court_decision | convention`. `amends_id` chains amendments to
the text they amend (walk it to reach the root). `citation` is the canonical
short cite ("Constitution (42nd Amendment) Act, 1976").

### instrument_edges  (aspect 1: offices)
Instrument → position. `relation`: `created_by | empowered_by | constrained_by |
abolished_by`. `provision` (required): the article/section ("Art. 52", "ss. 52,
64-68"). `scope` (nullable): the subject-matter/aspect condition — the hypergraph
lives here: `"forest offences on notified forest land"`, `"roads: land
acquisition / right-of-way"`, `"food: subsidized grain entitlement"`. The
`"<object>: <aspect> — <condition>"` convention makes object views queryable
(`scope LIKE 'roads:%'`).

### constitutional_controls  (aspect 1: the feedback web)
Controller position → controlled position. `mechanism`: `appoint | remove |
impeach | veto | assent | audit | review | supervise | dissolve | no_confidence`.
`instrument_id` + `provision` cite the source of the check. `note` carries the
**body-proxy convention**: chamber powers are anchored at the presiding office
("power of Parliament as a body, anchored at the Speaker") — never silently
attributed to one person. Checks are an overlay; do NOT count them as paths.

### division_kind_grants  (aspect 2: why boundaries overlap)
Which instrument created each *kind* of administrative division (municipality ←
74th Amendment; police organisation ← Police Act 1861 s. 4). One row per
(nation, kind, instrument, provision).

### domain_allocations  (aspect 3: who may even act)
Which LEVEL of government may act in each life-domain, per provision (India: the
Seventh Schedule — policing → State List Entry 2; forests → Concurrent 17A,
*inserted by the 42nd Amendment*, so allocation rows can cite amendments).
Multiple rows per domain express concurrent/split competence; `scope` carries
the aspect split ("roads: national highways" vs "roads: municipal streets").

### citizen_rights
What a person can invoke. `kind`: `fundamental | statutory | legal | absent`.
`legal` = demoted (India: Property, fundamental until the 44th Amendment, now
Art. 300A). `absent` rows have `instrument_id = NULL` — **the absence is the
fact** (no recall mechanism). `guarantor_slug` names the position to invoke
before; `limitation` is the honest fine print; `scope` bounds who/where it
applies ("rural households only — not inside municipal limits").

## Context tables (the office graph the genealogy grounds into)

| table | what |
|---|---|
| `positions` | offices: slug, name, branch, level, authority_basis, provenance |
| `position_domains` | office → life-domain + what it decides for a citizen |
| `dependencies` | office → office power flow (appointment/supervision/funding); provider → dependent |
| `delegations` | electoral origin: how the people delegate (directness = the citizen's leverage) |
| `personnel` | current officeholders (public officials only) |
| `divisions` / `position_divisions` | the overlapping boundaries and who serves each |
| `places` / `place_divisions` | citizen locations and which divisions cover them |
| `jurisdictions`, `nations` | the jurisdiction tree |

## Graph semantics (what `dag.py` does)

Power-granting path = `constitution → (amended_by | competence) → instrument →
(created_by | empowered_by) → office → (depends) → office → serves → division →
covers → place`. Statutes bridge to the constitution via a `competence` edge
labeled with the Seventh-Schedule-style allocation when known, else an explicit
generic legislative-competence label — the bridge is always visible.

Entrenchment class of an office = strongest terminal kind over its grant chains:
`constitution → constitutional`, `statute → statutory`, `charter → charter`,
`court_decision → interpretive`, `convention → uncodified`. A statutory office
empowered via a constitutional-amendment chain counts as constitutional (a
municipality via the 74th).

## Versioning

Dumps are immutable once published: `dumps/<country>-<MAJOR.MINOR.PATCH>/`.
PATCH = corrections; MINOR = new coverage (places, objects, rights); MAJOR =
format or semantic changes. `manifest.json` records version, counts, generation
time, and license. `SHA256SUMS` covers every file; releases are git-tagged and
the tag is signed by a maintainer (see CONTRIBUTING.md § signing).


## Internal office structure (v0.6.0+)

### office_posts
The post-types INSIDE an office. `position_id` -> the office; `post_name`
('Tehsildar', 'Section Officer', 'Peon'); `cadre` (IAS / state service /
ministerial / group-d); `rank` (0 = head, higher = lower); `decision_power`
(what they can SIGN/decide; empty or 'no decision' = moves files only);
`responsibility` (the citizen-facing action); `file_scope` (subject matter);
`instrument_id` + `provision` (the service rule / rules of business creating it).
Modeled as office-CLASS templates: one ladder instantiated across every office
of a class.

**Field replicas & `instance_count`.** Field posts (a Tehsildar per tehsil, a
Lekhpal per village, an SHO per station) recur many times in one office. The DB
holds every instance; the DUMP ships a small SAMPLE (a few rows per base post)
and records the true total in `instance_count` — so a 900-Lekhpal collectorate
is one row saying `instance_count: 900`, not 900 rows. Counts flagged this way
are ESTIMATES (medium confidence), scaled from typical district figures; a
contributor replaces them with their district's sanctioned strength. Analyzers
sum `instance_count` to report the real scale ("1,065 sanctioned posts").

### post_reports
The internal reporting ladder = the internal power structure (the COMMAND chain). `subordinate_id`
-> `superior_id` (both office_posts), `relation` (reports_to | delegated_by |
routes_files_to). Together with `rank`, this answers "who decides my file, and
who do they answer to inside the office."


### post_controls (v0.8.0+)
The INTERNAL feedback loops — the internal analog of `constitutional_controls`,
between post-types inside ONE office. Where `post_reports` is the command chain
(who instructs whom), this is the CHECK web: who AUDITS, VERIFIES, INSPECTS,
COUNTERSIGNS, SANCTIONS, or handles GRIEVANCE/APPEAL against whom.
`controller_id` -> `controlled_id` (both office_posts), `mechanism`
(audit|countersign|verify|inspect|sanction|vigilance|grievance|concurrence|
appeal|report_back), `scope` (what is checked), `provision` (the rule creating
the check — e.g. UP Land Records Manual, Financial Handbook, Police Regulations).
Modeled once per office between the representative post-types (a check on a
cadre, not on each of 900 replicas). Example: the Treasury Officer AUDITS the
Nazir's cash; the Sadar Kanungo AUDITS the Lekhpal's land records; the Circle
Officer INSPECTS the SHO's station.

## Task flows (v0.9.0+) — the process layer

`task_flows` + `task_steps` answer "how do I get X done." A flow is a citizen
task (land-mutation, caste-certificate, building-permit, ration-card,
rte-admission, mgnrega-work) with `office_class`, `legal_basis`, `total_days`,
`citizen_input`, `outcome`. `task_steps` are the ORDERED steps: `step_no`,
`post_name` (links to office_posts — a flow is a path through the office's
posts), `action`, `step_kind` (submit/verify/inspect/decide/approve/sign/
deliver/check/escalate), `is_approval` (does this step decide the request),
`time_limit` (statutory), `on_reject` (appeal/escalation path). This is the
payoff: structure (offices/posts/checks) + process (flows/steps) = an
answerable "who does what, in what order, with what recourse" workflow.

## Stable external IDs (v0.11.0+) — how to reference a role

The `id` columns are per-dump SERIALs, REASSIGNED on every rebuild — never cite
them. Every role-bearing row also carries a `stable_id`: a deterministic,
content-derived URN identical across every dump, so an external document can
durably reference a specific role, check, or process step.

| table | stable_id form | example |
|---|---|---|
| positions | `slug` (already stable) | `in-pauri-garhwal-dm` |
| office_posts | `role:<nation>/<office-slug>/<post-slug>[#N]` | `role:in/in-pauri-garhwal-dm/tehsildar#1` |
| post_reports | `reports:<nation>/<office>/<sub>>-<sup>` | reporting edge |
| post_controls | `check:<nation>/<office>/<controller>--<mechanism>-><controlled>` | `check:in/.../kanungo-supervisor#14--verify->lekhpal-patwari#136` |
| task_flows | `flow:<nation>/<task-slug>` | `flow:in/land-mutation` |
| task_steps | `step:<nation>/<task-slug>/<step-no>` | `step:in/land-mutation/4` |

The `#N` on a role is the replica index (a district has many Tehsildars);
`#1` is the representative. Regenerated by `app.assign_stable_ids` (idempotent,
deterministic). Validators enforce presence and uniqueness of `office_posts.stable_id`.

## Universal Role Schema (Core v1) export (v0.12.0+)

Alongside the dump, an optional `role_spec/<version>/` directory carries an
organization-agnostic projection of every office and internal post — the format
any government/company/NGO/military could adopt so their structures interoperate.
Full spec in [ROLE_SPEC.md](ROLE_SPEC.md); this is the at-a-glance shape:

- `roles.jsonl` — the ~15-field core record per role. `role_id` reuses the stable
  URN (office = `role:<n>/<office>`, post = `role:<n>/<office>/<post>`), so a
  post's id is literally its office's id plus a path segment. Rich data is by
  reference: `responsibility_ids`, `authority_ids`, `control_ids`, `source_ids`,
  `capabilities`. `performed_by` = `{type, automation}`; `confidence` is a float
  in `[0,1]` (high→0.9, medium→0.6, low→0.3).
- linked entities, each keyed by a content-hash id (identical content = one row):
  `organizations.jsonl` (`ORG:<slug>`), `responsibilities.jsonl` (`RESP-<hash>`),
  `authorities.jsonl` (`AUTH-<hash>`), `controls.jsonl` (`CTRL-<hash>`),
  `sources.jsonl` (`SRC-<hash>`), `capabilities.jsonl` (`CAP-<name>`, controlled
  vocabulary).

Generated by `app/export_role_spec.py`; read with `dag.py role-spec <dir>`;
`validate.py --role-spec <dir>` enforces the contract (enum vocabularies, `[0,1]`
confidence, referential integrity, unsourced-claim = low-confidence).