# Changelog

## india-0.7.0 (2026-07-24)

**Full internal office structure at real scale — from the DM to the peon, and
every one of the ~900 Lekhpals.** Six office-class templates, researched from
actual service rules by fan-out agents, instantiated across every matching
office: 322 -> 278,390 sanctioned posts across 508 offices.

- district-collectorate (40 post-types): DM/ADM/SDM/Tehsildar/Lekhpal/nazarat/
  treasury/establishment - ~1,065 posts per collectorate (UP LR Act, BNSS/CrPC,
  Financial Handbook, Manual of Office Procedure)
- police-district (25): SP/CO/SHO/SI/constable + reserve/traffic/crime/malkhana
  - ~375 posts per district (Police Act 1861, Police Regulations, CrPC)
- rural-panchayat (24): Zila/Kshettra/Gram tiers + BDO/VDO/Rozgar Sevak
  (Part IX, Panchayat Raj Act, MGNREGA)
- district-court (27): D&S Judge -> magistrates -> Nazir/Ahlmad/process server
  (Arts.233-237, District Court Service Rules)
- municipal-corporation (27) & secretariat-department (15) rebuilt richer;
  district-health (23) added
- Each post carries cadre, decision power (who SIGNS vs who moves files),
  citizen-facing responsibility, file scope, reporting line, and the service
  rule grounding it.
- Dump uses `instance_count` sampling: field replicas collapse to a few sample
  rows carrying the true total, keeping the dump at 14 MB (was 162 MB raw) and
  git/browser-friendly. Analyzers and the 3D viewer sum it to show real scale.
- Non-pollution holds (internal tables never touch the power engine).

## india-0.6.0 (2026-07-24)

**Inside the office: the internal power structure.** Grounding and effect map
the office as a point; this opens it up. Every office now contains a LADDER of
post-types — from the IAS head down to the peon — each with its decision power,
responsibility, file scope, and reporting line.

- Two tables: `office_posts` (the post-types of an office) and `post_reports`
  (the internal reporting ladder = the internal power structure).
- Modeled as office-CLASS templates (same doctrine as office grounding, one
  level deeper): one template describes the ladder of ALL ~99 District
  Collectorates, ~103 police districts, ~64 municipal corporations, ~50
  secretariat departments. 322 offices x their ladder = 2,569 posts, 2,247
  reporting edges. Each post grounded in the service rule / rules of business
  that creates it (Tehsildar -> UP LR Act; SHO -> CrPC ss.154-157; Section
  Officer -> manual of office procedure).
- `dag.py inside "<office>"` renders the ladder; the 3D viewer's office panel
  gains "open the interior" to drill into the post structure.
- Decision power is explicit per post: who can SIGN (DM, Tehsildar, SHO) vs who
  only moves files (Section Officer, Dealing Assistant, Peon) — the citizen's
  real question of "who actually decides my file" is now answerable.
- Non-pollution invariant holds: internal-structure tables never touch the
  power engine (asserted). validate.py enforces post/report integrity.

## india-0.5.0 (2026-07-24)

**The grounding invariant: every live office now reaches the Constitution.**
0 ungrounded (was 489 in 0.4.0; 96% of the dump two versions ago). Achieved in
two honest stages, never by fabrication:

- Specific rules (+124): Union ministries/ministers (Art. 74-75, 77), state
  ministers (Art. 163-164, 166), High Courts (Art. 214-217), municipal organs
  (Art. 243Q/243W + Twelfth Schedule), panchayat organs (Art. 243B-243G).
- Channel grounding (+384, medium confidence): offices whose specific creating
  statute is not yet identified are grounded through the constitutional channel
  their authority actually flows through — Union executive power (Art. 53, 73,
  77(3)), state executive power (Art. 154, 162, 166(3)), or the legislature/
  judiciary Parts. The note on every such edge states the backlog explicitly.
  This is TRUE but unspecific — upgrading channel grants to named statutes is
  the standing contribution opportunity.
- validate.py now enforces the invariant: ungrounded live offices warn in PR
  mode and BLOCK --strict releases. india-0.5.0 passes strict with 0 warnings.

## india-0.4.0 (2026-07-24)

Coverage pass — answering "are these all the nodes?" with a census and two
mass additions:

- `coverage.py`: the incompleteness census (depth per state, repeating office
  TEMPLATES, bare division kinds, grounding backlog). It found the lever: the
  dump's offices cluster into 32 repeating templates whose creating provisions
  are uniform.
- **Template grounding** (nationAtlas `app/ground_templates.py`): 9 rules
  grounded 625 offices in one pass — every District Magistrate (CrPC ss.
  107-144), SP (Police Act s. 4), District & Sessions Court (Art. 233-237),
  Public Prosecutor (CrPC s. 24), Sarpanch/Zila Parishad (Art. 243B), municipal
  commissioner/council (Part IXA). Grounding backlog: 96% -> 42%.
- **National regulators** (+7 offices, +7 instruments): RBI Governor (RBI Act
  1934 s. 8), SEBI, TRAI, CPCB, EPFO CPFC, Railway Board, and the CBI Director
  with its tripartite PM+LoP+CJI selection (DSPE Act s. 4A) — the third
  independence design (committee appointment) now in the control web.
- Known artifact: the pivot path enumeration hits the 400-path cap, which
  undercounts "grounded via path membership" — the census's direct grounding
  count is authoritative.

## india-0.3.0 (2026-07-24)

Part XVIII (Emergency) + Part IX (Panchayats) read + loop-closing pass:

- President's rule (Art. 356) as the Union's heaviest check on a state —
  President dissolve -> state CM, Governor's report as trigger, both edges
  carrying the S.R. Bommai (1994) judicial-review constraint (new
  court_decision instrument)
- 44th Amendment's emergency tightening as a constrained_by edge ('armed
  rebellion' standard, written cabinet advice) — the 42nd/44th axis now spans
  advice, property AND emergency
- Part IX grounding for the discovered panchayat institutions (Art. 243B +
  UP Panchayat Raj Act 1947 / Kshettra-Zila Adhiniyam 1961) with SEC election
  supervision (Art. 243K)
- Loop-closing: FSSAI (FSS Act s. 5), consumer commission (CPA s. 42(3)),
  civil supplies (NFSA ss. 14-15), CMO, mandi board; education chain
  (Art. 164(1) + UP Basic Education Act); MH HC chief (Art. 217 collegium);
  and the classic DUAL CONTROL: district police under the DM's general control
  and direction (Police Act 1861 s. 4)
- Pivot loop completeness 0.974 with a SINGLE honest gap: the GST Council
  chair, whose weighted-mutual-voting control (Art. 279A(4)) is a shape the
  mechanism vocabulary cannot yet express — recorded as a format TODO
- +3 instruments (Bommai, UP Panchayat Raj Act 1947, UP KP/ZP Adhiniyam 1961),
  +8 edges, +18 controls total across the pass

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
