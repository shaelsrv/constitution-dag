# Building your country's map — agents, infra, and the nurture loop

You need: Python 3.10+, a text editor, optionally an LLM assistant (any model,
local models work), and access to your country's legal texts online. A database
is optional — dumps are plain JSONL you can edit by hand.

## Stage 0 — pick your pivot

Pick ONE real place you know personally (your town). Everything is built and
tested against it. A map grounded in one real place beats a vague national map:
wrong facts become *visible* ("that's not my constituency") instead of surviving
as plausible noise. Our pilot pivot is Kotdwar, Uttarakhand, India.

## Stage 1 — the seed DAG (a weekend of curation)

Author these rows by hand (LLM as drafting assistant, you as the authority):

1. **The root**: your constitution as a `legal_instruments` row
   (`kind=constitution`). No codified constitution? Use `kind=convention` +
   the founding statutes — the schema supports uncodified systems.
2. **Landmark amendments** (3–6): the ones that moved power. Chain them with
   `amends_id`. For each, add at least one `constrained_by` or `empowered_by`
   edge — power REMOVED is as important as power granted.
3. **~12 apex offices** as `positions` + their `instrument_edges`
   (`created_by` with the exact article). Include the head of state, head of
   government, top court, auditor, election body, one state/province chain.
4. **The famous feedback loops** (10–15 `constitutional_controls`): who
   impeaches the head of state, who can dissolve what, who audits whom, who
   reviews legislation. Use the body-proxy convention (SCHEMA.md) for chamber
   powers. Aim for **zero unwatched watchers**: every controller should itself
   be controlled by someone — if you can't find the check, your constitution
   may genuinely lack it, which is a finding; record it in your notes.
5. **One local chain**: your town as a `places` row, its divisions
   (municipal / electoral / district / state), the offices serving each, and
   the statutes that created them (`competence` bridging happens automatically
   via `domain_allocations`).
6. **Domain allocations**: your constitution's competence map (India: Seventh
   Schedule; Germany: Arts. 70–74; US: enumerated powers + 10th Amendment).
7. **The rights ledger** (10–12 `citizen_rights`): fundamental vs statutory,
   each with its guarantor office and honest limitation — and at least one
   `demoted` and one `absent` row. Every polity has both; finding them is the
   test that you looked.

Validate continuously:

```bash
python dag.py dumps/yourcountry-0.1.0 paths your-town
```

The "no known constitutional path" list is your to-do list. When it's empty and
the meets look right, you have a seed.

## Stage 2 — the nurture loop

Repeat forever; each cycle makes the map truer:

1. **Scan** — run the paths/objects/rights reports; note gaps and oddities.
2. **Adversarial pass** — pick claims where your data disagrees with itself or
   with your local knowledge, and check them against PRIMARY sources
   (legislation portals, gazettes, official municipal sites, court judgments).
   Hard-won lesson from the pilot: **LLM verifier votes are not a source.**
   Two grounded models refuted a true fact about our pilot town's municipal
   status and confirmed two mutually exclusive constituency claims — the web
   sources settled it in one search. Use LLMs to *propose* and *draft*; use
   retrieval to *verify*. And make your verification fail-closed: an errored
   check is "unverified", never "confirmed".
3. **Fix forward** — corrections keep an audit trail: append what changed and
   why to a ledger file (we use JSONL ledgers: `merge_ledger`,
   `deprecation_ledger`, `jurisdiction_fixes`). Wrong rows get *deprecated with
   a reason*, not silently deleted — someone may have cited them.
4. **Enrich by object** — pick an object your town cares about (water, roads,
   food, schools, land) and add its scoped edges: `"water: supply — municipal
   limits"`, `"water: irrigation canals — state"`, `"land: mutation records —
   district"`. Five to eight edges per object is a full picture.
5. **Version and publish** — bump the dump version, regenerate SHA256SUMS,
   tag, release.

## Agent prompt patterns (LLM-assisted drafting)

**Discovery draft** (output is ALWAYS a candidate, confidence=low):

> List the offices that govern <domain> for a resident of <place, region,
> country>, from most local to national. For each: official office title (not
> the person), the statute or constitutional article that creates it, and what
> it decides for a resident. Strict JSON. Omit anything you cannot name a legal
> basis for.

**Provision check** (the verification step — requires retrieval/browsing):

> Here is the claim: "<office> is created/empowered by <instrument>
> <provision>". Retrieve the text of <provision> from an authoritative source
> (legislation portal, gazette). Quote the operative words. Answer:
> supported / not supported / provision not found — with the URL.

**Control-loop probe**:

> For the office <X> in <country>: who can remove, suspend, or override it, and
> under which provision? Who audits it? Whose approval does it need for budget?
> Cite provisions. If no removal mechanism exists, say so explicitly — the
> absence is the answer.

**Scope split probe** (the object lens):

> For <object> in <place>: list the distinct legal aspects (creation/
> classification, land, standards, usage, fees, enforcement) and for each the
> office + instrument + provision that holds it. Same object, different aspects,
> different masters.

Tier your models by role: cheap/local models for discovery drafts (they're
disposable), your best retrieval setup for verification (it lands in the data).

## Infra options

- **Just files**: edit the JSONL dumps directly; `dag.py` needs nothing else.
- **The full instrument**: the parent project (nationAtlas) runs this schema on
  Postgres with a FastAPI atlas UI, verification pipelines, and self-hosting on
  local models (Ollama) for censorship resilience. Its genealogy tables match
  this dump format 1:1; `app/export_dag_dump.py` produces these dumps.
- **Your own**: anything that can read JSONL and emit it back. Keep the format;
  the format is the collaboration contract.
