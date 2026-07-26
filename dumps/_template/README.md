# `_template` — a validates-green starter dump

This is a **fictional** minimal country ("Republic of Riverland") that already
passes `validate.py` with 0 errors and produces a full paths / rights / scan
report. It exists so you don't start from a blank page: **copy it, then replace
every row with your real country.**

```bash
# from the repo root — copies this into dumps/<your-country>-0.1.0/
python newdump.py new mycountry

# ...edit dumps/mycountry-0.1.0/*.jsonl to your real constitution and offices...

python newdump.py stamp dumps/mycountry-0.1.0     # refresh manifest + checksums
python validate.py dumps/mycountry-0.1.0          # must say 0 errors
python dag.py dumps/mycountry-0.1.0 paths <your-town>
```

## What each file shows (all fictional — replace them)

| file | rows | the pattern it demonstrates |
|---|---|---|
| `nations.jsonl` | 1 | your country + its `govt_type` |
| `legal_instruments.jsonl` | 3 | constitution (root) + an amendment (`amends_id` chains to it) + a statute |
| `positions.jsonl` | 5 | 4 apex offices + 1 local office (the mayor of your town) |
| `instrument_edges.jsonl` | 6 | every office **grounded** to the constitution via `created_by`/`empowered_by` + the exact `provision`; the mayor reaches the constitution **through the amendment** |
| `constitutional_controls.jsonl` | 5 | the feedback web — appoint, advise, audit, review — wired so **no watcher is unwatched** (the court reviews the auditor) |
| `citizen_rights.jsonl` | 2 | one `fundamental` right **and** one `absent` right (the absence is data) |
| `divisions` / `places` / `place_divisions` / `position_divisions` | — | the local chain: your town → its divisions → the offices that serve each |
| `division_kind_grants` / `domain_allocations` | 1 each | why a division kind exists; which level may act in a domain |
| `dependencies` / `position_domains` | 0 | present-but-empty; fill as you grow |

## The three rules that keep it trustworthy

1. **Provenance on every row.** Keep `source` + `confidence`. `high` is *earned*
   by checking the primary text; unverified act-level attributions are `medium`.
2. **Aim for zero unwatched watchers.** Run `python scan.py <dump> --pivot <town>` —
   every `unwatched-watcher` hit is a control you haven't found yet (or a genuine
   gap in your constitution, which is itself a finding).
3. **`paths` shows your to-do list.** Any office under "no known constitutional
   path" isn't grounded yet — that list *is* your work queue.

When your report looks right and the meets make sense, you have a seed. Then
follow [AGENTS.md](../../AGENTS.md) Stage 2 to nurture it.
