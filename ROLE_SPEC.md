# Universal Role Schema — Core v1

A minimum, organization-agnostic specification for describing a **role**: a unit of
responsibility inside any organization — a government office, a company job, an NGO
position, a military billet, a university post, or a future AI/robotic agent.

The goal is interoperability. If a national government, a corporation, and a nonprofit
all export their org structure in this shape, the three become one queryable graph:
*"show every role in any organization that can approve a payment"*, *"trace who a
citizen's request passes through"*, *"which roles are candidates for automation"* —
answerable across sources that never coordinated.

This spec is deliberately small. The **core role record is ~15 fields**; everything
richer (the text of a responsibility, the wording of an authority, the citation of a
source) lives in **linked entities** referenced by ID, never embedded. That is what
keeps the core stable across decades while the world underneath it changes.

> This is a projection format, not a new data-collection burden. Any system that
> already models who-does-what can emit it. The constitution-dag pilot generates it
> from data it already holds (`app/export_role_spec.py`).

---

## Design rules

1. **Small stable core, linked rich entities.** The 15 core fields are the contract.
   Responsibilities, authorities, controls, and sources are separate records with
   their own IDs; the role holds *lists of IDs*, never the text. Two roles that share
   a responsibility share one `RESP-…` id — dedup is free, and correcting the text in
   one place corrects it everywhere.
2. **Every ID is durable and content-derived.** `role_id` is a permanent, globally
   unique handle — a DOI for a public role. Linked-entity IDs are content hashes, so
   the same responsibility always gets the same `RESP-…` id across dumps and across
   organizations. IDs survive rebuilds; integer row-ids do not and are never cited.
3. **`performed_by` is first-class, not an afterthought.** A role can be performed by
   a human, an AI agent, a robot, or a hybrid team. Recording *what performs the role*
   in the core — separately from *what the role is* — is what lets the schema stay
   valid as a role migrates human → hybrid → automated without changing its identity.
4. **Confidence and source travel with every role.** A role asserts nothing without a
   `confidence` in `[0,1]` and a list of `source_ids`. `high` (≥0.9) is *earned* by
   verification against a primary authority, never self-declared.
5. **Capabilities are a controlled vocabulary, not free text.** The capability profile
   is what makes cross-organization queries work ("every role doing physical
   inspection"), so its terms are enumerated and shared, not per-org prose.

---

## The core role record (15 fields)

| # | Field | Req | Type | Meaning |
|---|---|---|---|---|
| 1 | `role_id` | ✅ | URN string | Permanent, globally unique handle. Stable across every dump. |
| 2 | `dump_version` | ✅ | semver | The dataset version this record was emitted in. |
| 3 | `revision_id` | ✅ | string | Immutable revision of *this role* (defaults to `dump_version`). |
| 4 | `name` | ✅ | string | The role's title — the office, not the person. |
| 5 | `organization_id` | ✅ | `ORG:…` | The organization that contains this role. |
| 6 | `status` | ✅ | enum | `active \| vacant \| retired \| merged \| split \| abolished \| planned` |
| 7 | `role_type` | ✅ | enum | `elected \| appointed \| employee \| contractor \| ai_agent \| robot \| hybrid` |
| 8 | `parent_role_id` | — | `role:…` | The role this one reports to (org ladder). |
| 9 | `purpose` | ✅ | string | One sentence: *why this role exists.* |
| 10 | `responsibility_ids` | ✅ | `[RESP-…]` | What the role is accountable for (by reference). |
| 11 | `authority_ids` | — | `[AUTH-…]` | What the role may decide/sign (by reference). |
| 12 | `control_ids` | — | `[CTRL-…]` | Checks *on* this role — who audits/removes/reviews it. |
| 13 | `performed_by` | ✅ | object | `{type, automation}` — human / ai / robot / hybrid. |
| 14 | `capabilities` | ✅ | `[CAP-…]` | Capability profile from the shared vocabulary. |
| 15 | `effective_from` | ✅ | date/`unknown` | When the role took its current form. |
| — | `effective_to` | — | date/null | When it ended (null = still in force). |
| 16 | `source_ids` | ✅ | `[SRC-…]` | Evidence backing this record. |
| 17 | `confidence` | ✅ | float `[0,1]` | Verification strength. `high`=0.9, `medium`=0.6, `low`=0.3. |

(`effective_to` and the optional reference lists round the record to a stable shape;
"~15" counts the always-present fields.)

### `performed_by`

```json
{ "type": "human", "automation": "human_only" }
```

- `type`: `human | ai | robot | hybrid`
- `automation`: `human_only | human_in_the_loop | supervised_autonomy | full_autonomy`

The same role identity survives a change here. A "Document Verification Officer" that
moves from `human_only` to `human_in_the_loop` (AI drafts, human signs) to
`supervised_autonomy` keeps its `role_id`, `purpose`, and `responsibility_ids`; only
`performed_by` changes, revision by revision. That is the point of separating *what the
role is* from *what performs it*.

### `capabilities` — the shared vocabulary

Each capability is a `CAP-<name>` reference into `capabilities.jsonl`. The controlled
set (extend by proposal, never ad hoc):

`physical_inspection`, `financial_approval`, `policy_analysis`, `investigation`,
`procurement`, `public_communication`, `legal_review`, `compliance`, `record_keeping`,
`emergency_response`, `service_delivery`, `supervision`, `administration`.

This is what powers the cross-cutting queries: *"every role involving physical
inspection"* (1,723 in the India pilot), *"every role that can approve funds"* (3,390),
*"every role suitable for robotic automation"* (filter capabilities × `performed_by`).

---

## Linked entities

Each is a JSONL file of records keyed by a content-hash ID, so identical content
collapses to one row and stays stable across dumps.

| Entity | File | ID | Fields |
|---|---|---|---|
| Organization | `organizations.jsonl` | `ORG:<slug>` | `name`, `level`, `branch` |
| Responsibility | `responsibilities.jsonl` | `RESP-<hash>` | `text`, `confidence` |
| Authority | `authorities.jsonl` | `AUTH-<hash>` | `decision`, `provision`, `confidence` |
| Control | `controls.jsonl` | `CTRL-<hash>` | `mechanism`, `exercised_by_role_id`, `scope`, `provision` |
| Source | `sources.jsonl` | `SRC-<hash>` | `citation` |
| Capability | `capabilities.jsonl` | `CAP-<name>` | `name` |

A **Control** is not a grant — it is a check *on* a role (audit, remove, review,
countersign, sanction), carrying who exercises it (`exercised_by_role_id`), over what
scope, under which provision. Keeping controls separate from authorities is what lets
"who can approve" and "who checks the approver" stay distinct queries.

---

## The graph it forms

```
Organization ──contains──▶ Role ──has──▶ Responsibility
                            │  ├──may exercise──▶ Authority
                            │  ├──is checked by──▶ Control ──exercised by──▶ Role
                            │  ├──performed by──▶ {human | ai | robot | hybrid}
                            │  ├──has profile──▶ Capability
                            │  └──backed by──▶ Source
                            └──reports to──▶ Role (parent_role_id)
```

Load `roles.jsonl` as nodes and the four reference lists as typed edges, and you have a
property graph any store (Neo4j, DuckDB, RDF, plain pandas) can traverse.

---

## Example — a real role

```json
{
  "role_id": "role:in/in-pauri-garhwal-dm/tehsildar",
  "dump_version": "0.12.0",
  "revision_id": "0.12.0",
  "name": "Tehsildar",
  "organization_id": "ORG:in-pauri-garhwal-dm",
  "status": "active",
  "role_type": "appointed",
  "parent_role_id": null,
  "purpose": "head of the tehsil; land records, revenue collection, certificates",
  "responsibility_ids": ["RESP-18a4557803f3"],
  "authority_ids": ["AUTH-f18b8a70b5b2"],
  "control_ids": null,
  "performed_by": { "type": "human", "automation": "human_only" },
  "capabilities": ["CAP-legal_review", "CAP-compliance", "CAP-record_keeping",
                   "CAP-supervision"],
  "effective_from": "unknown",
  "effective_to": null,
  "source_ids": ["SRC-a748289633ef"],
  "confidence": 0.6
}
```

`RESP-18a4557803f3` resolves in `responsibilities.jsonl` to *"head of the tehsil;
land records, revenue collection, certificates"*; `AUTH-f18b8a70b5b2` to the Circle
Revenue Officer powers under the UP Land Revenue Act; `SRC-a748289633ef` to that Act.
Any other Tehsildar office across the dataset that shares that responsibility text
points at the *same* `RESP-…` id.

---

## Emitting the format

Any organization can produce a conforming export by mapping its own fields onto the 15:

| Your data | → Core v1 field |
|---|---|
| stable job/office code | `role_id` (mint a URN if you lack one) |
| job title | `name` |
| department / entity | `organization_id` |
| mission statement | `purpose` |
| duties (as separate records) | `responsibility_ids` |
| sign-off / delegation authority | `authority_ids` |
| audit/oversight relationships | `control_ids` |
| filled by person / bot / team | `performed_by` |
| classification (elected/hired/…) | `role_type` |
| effective date | `effective_from` |
| policy/law/HR-doc references | `source_ids` |
| how well-verified | `confidence` |

The pilot's generator is `app/export_role_spec.py` in the nationAtlas repo; run
`python dag.py <dump> role-spec` (see below) to read a conforming export, or point any
JSONL reader at the files.

---

## Validation

A conforming `role_spec/` directory MUST satisfy:

- every `role_id` unique within the export;
- every referenced `RESP-`/`AUTH-`/`CTRL-`/`SRC-`/`CAP-`/`ORG:` id present in its file;
- every role carries `confidence ∈ [0,1]` and ≥1 `source_id` (or explicit `confidence`
  ≤ 0.3 declaring the gap);
- `status`, `role_type`, `performed_by.type`, `performed_by.automation`, and every
  `capabilities` term drawn from their enumerated vocabularies;
- `manifest.json` present with `format: "role-spec/core-v1"`, `version`, `counts`.

`validate.py` in this repo enforces these when a `role_spec/` directory is present.

---

## Why these choices

- **Why IDs, not embedded text?** Text drifts and duplicates. A role that references
  `RESP-18a4…` inherits every future correction to that responsibility, and a query can
  count *distinct* responsibilities without string-matching prose.
- **Why is `performed_by` in the core?** Because the interesting longitudinal question
  of the next decades is *which roles move from human to machine*, and you cannot ask it
  if "who performs this" is buried in a sub-table. Putting it in the core makes the
  human→AI→robot transition a first-class, queryable fact.
- **Why a capability vocabulary?** Titles don't compare across organizations ("Deputy
  Secretary" means nothing to a company), but *capabilities* do. A shared, small,
  controlled vocabulary is the join key that makes a government office and a corporate
  role commensurable.
- **Why keep it to ~15 fields?** Every field in the core is a field every adopter must
  fill. Anything not universal belongs in a linked entity, where it's optional and
  extensible. The core is a promise; the entities are where richness grows without
  breaking the promise.

---

*Part of [constitution-dag](./README.md). Spec: CC-BY 4.0. Reference implementation
(`app/export_role_spec.py`) and validator: MIT.*
