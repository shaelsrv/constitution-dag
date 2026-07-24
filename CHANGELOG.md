# Changelog

## india-0.2.0 (2026-07-24)

Constitutional-completeness pass — the Constitution's own structural map read
back against the data (articles cross-checked against published
constitutional-bodies references):

- +9 offices the Constitution itself creates that were missing: Vice-President
  (Art. 63-68), Attorney-General (Art. 76), Governor of Uttarakhand (Art.
  153-156), Advocate-General UK (Art. 165), UPSC Chairman (Art. 315-320,
  removal via SC inquiry Art. 317), Finance Commission Chairman (Art. 280),
  GST Council Chair (Art. 279A / 101st Amendment 2016), NCSC Chairman
  (Art. 338), State Election Commissioner UK (Art. 243K/243ZA)
- +15 control edges closing their loops — incl. the structurally important
  SEC fact: the Mayor's election answers to the STATE Election Commission,
  not the ECI (Art. 243ZA)
- +7 domain allocations: EVERY domain in the 24-domain vocabulary now has a
  constitutional allocation, incl. taxation-via-GST (Art. 246A/279A — the
  101st Amendment as a domain-level power shift)
- +3 Part III rights: Art. 17 (untouchability), Art. 23 (forced labour),
  Art. 24 (child labour) with district-level guarantor offices
- +2 instruments (86th Amendment 2002, 101st Amendment 2016)
- pivot: 47/47 Kotdwar-serving offices grounded

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
