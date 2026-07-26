# Building your country's map — agents, infra, and the nurture loop

You're building the substrate for accountability: a navigable, source-backed map
of who holds what public authority, so real public actions can one day be pinned
to the exact role and control behind them. It starts with one town you know.

You need: Python 3.10+, a text editor, optionally an LLM assistant (any model,
local models work), and access to your country's legal texts online. A database
is optional — dumps are plain JSONL you can edit by hand.

## Stage 0 — pick your pivot

Pick ONE real place you know personally (your town). Everything is built and
tested against it. A map grounded in one real place beats a vague national map:
wrong facts become *visible* ("that's not my constituency") instead of surviving
as plausible noise. Our pilot pivot is Kotdwar, Uttarakhand, India.

## Stage 1 — the seed DAG (a weekend of curation)

**Don't start from a blank page.** Copy the validates-green starter template — it's
a tiny fictional country that already produces a full report, so you edit rather
than invent the format:

```bash
python newdump.py new mycountry          # -> dumps/mycountry-0.1.0/ (a working skeleton)
# ...edit the .jsonl files to your real country (guide: dumps/_template/README.md)...
python newdump.py stamp dumps/mycountry-0.1.0    # refresh manifest + SHA256SUMS after every edit
python validate.py dumps/mycountry-0.1.0         # must say 0 errors
python dag.py dumps/mycountry-0.1.0 paths <your-town>
```

`newdump.py stamp` regenerates `manifest.json` + `SHA256SUMS` for you — never
hand-maintain those. Exact field-by-field shapes for every table are in
[SCHEMA.md](SCHEMA.md) and shown live in `dumps/_template/`. Then author your rows
(LLM as drafting assistant, you as the authority):

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

## Stage 3 — go deeper: inside the office, and how a citizen gets things done

Stages 1–2 give the constitutional genealogy (offices, controls, rights,
objects). The pilot then added four more layers, in this order — each is
optional but each makes the map far more useful. Format details are in
SCHEMA.md; the tables are `office_posts`, `post_reports`, `post_controls`,
`task_flows`, `task_steps`.

1. **Internal office structure** (`office_posts` + `post_reports`). An office is
   a container; inside it is a ladder of post-types — a District Magistrate's
   office holds the ADM, SDM, Tehsildar, Lekhpal, Section Officer, peon…
   Model the recurring post-types once per office **class** (all district
   collectorates share a ladder) and instantiate across every matching office;
   `post_reports` is the reporting chain. Each post carries its `decision_power`
   (who can SIGN vs who only moves files), `responsibility`, and the service
   rule that creates it. Field posts that recur (a Lekhpal per village) are
   modeled with an `instance_count` estimate rather than 900 literal rows.
2. **Internal feedback loops** (`post_controls`). The internal analog of
   `constitutional_controls`, between post-types inside one office: who audits,
   verifies, inspects, countersigns, or sanctions whom (the Treasury Officer
   audits the Nazir's cash; the Kanungo verifies the Lekhpal's entries). Same
   "checks are not grants" discipline — these are a separate layer from the
   command ladder.
3. **Task flows** (`task_flows` + `task_steps`) — the payoff. The ordered
   step-by-step process for a real citizen task ("how do I get a land mutation /
   ration card / building permit done"): each step names the post-type that
   performs it, whether it's an approval, the statutory time limit, and the
   appeal path if rejected. A flow is a *path through the office's posts*.
   Ground every step in the governing Act and the state Right-to-Public-Services
   schedule.
4. **Stable external IDs**. The per-dump integer `id`s are reassigned on every
   rebuild, so they can't be cited. Give every role-bearing row a deterministic
   content-derived URN (`role:<nation>/<office>/<post>#N`, `check:…`, `flow:…`,
   `step:…`) that is identical across dumps — see SCHEMA.md § "Stable external
   IDs". In the pilot this is `app.assign_stable_ids`; if you build by hand, use
   the same URN scheme so downstream references stay durable.

### The enrichment loop (scaling task flows)

Task-flow coverage scales through a three-agent loop, which is worth reusing:
**(1) generate** candidate citizen questions across life-domains (dedup against
what you already cover); **(2) answer** each from structural knowledge only, no
search, flagging every uncertainty; **(3) review + enrich** — web-search the
governing rules, correct the draft, fill gaps, return a source-grounded flow.
The reviewer is the one that retrieves and corrects — the same propose/verify
discipline as the nurture loop, one layer up. Run it in rounds, accumulating
against a covered-set so nothing duplicates. (Pilot implementation:
`pipelines/task_flow_enrichment.workflow.js` in the nationAtlas repo.)

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
