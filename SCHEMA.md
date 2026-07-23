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
