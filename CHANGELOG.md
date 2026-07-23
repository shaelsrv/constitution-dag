# Changelog

## india-0.1.1 (2026-07-22)

Integrity fix, caught by the new `validate.py` on its FIRST run (layer-0 gate
working as designed): the 0.1.0 exporter dropped divisions that cover a place
but have no serving office yet — 37 broken `place_divisions` references.
0.1.1 exports the full referenced-division union (+37 divisions). 0.1.0 stays
published as the honest record; downstream users should pin 0.1.1.

Also added: `validate.py` (mechanical quality gate), `QUALITY.md` (the five-layer
enforcement stack), CI workflow, `pivots.json` (falsifiability registry),
`ledgers/corrections.jsonl`.

## india-0.1.0 (2026-07-22)

First public dump. India pilot, pivot city Kotdwar (Uttarakhand):

- 29 legal instruments (Constitution of India 1950; 42nd/44th/73rd/74th
  Amendments; UP Municipal Corporation Act 1959 + Uttaranchal 2002 adaptation;
  Forest Act 1927; Police Act 1861; CrPC 1973; NH/NHAI/MV/RFCTLARR Acts;
  RTI/RTE/NFSA/MGNREGA/FSS/CPA; Kesavananda + Second/Third Judges Cases)
- 50 instrument->office grants with provisions + aspect scopes
  (roads: 5 aspects / 4 offices; food: 5 aspects / 5 offices)
- 27 constitutional control edges (impeach/assent/no-confidence/audit/review);
  zero unwatched watchers in the curated web
- 26 domain allocations (Seventh Schedule, incl. the 42nd Amendment's
  education/forests/justice moves), 10 division-kind grants
- 12 citizen rights incl. 1 demoted (Property, 44th Amdt -> Art. 300A) and
  1 absent (no recall mechanism)
- context graph: 1,144 offices / 110 places / 4,565 dependency edges
- pivot validation: 44/44 offices serving Kotdwar trace to the Constitution

Known limitations (welcome first contributions): contact/timeline data not
included; several statute attributions at confidence=medium (act-level, not
section-verified); rights guarantors for RTI/MGNREGA are district-nodal
approximations; only one pivot city is deeply validated.
