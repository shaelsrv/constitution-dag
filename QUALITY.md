# Quality & accuracy enforcement

"Enforce" means gates that actually block, not norms we hope for. The stack has
five layers; each catches what the layer above it cannot.

## Layer 0 — mechanical validation (CI, blocks every merge)

`python validate.py <dump>` runs on every PR (see `.github/workflows/validate.yml`)
and fails the build on:

- malformed rows, missing required fields, out-of-vocabulary enums
- broken referential integrity (any id that doesn't resolve inside the dump)
- duplicate rows against the declared UNIQUE keys
- provenance violations: genealogy rows without `confidence`; **`confidence=high`
  without a source** (high is earned, never declared)
- honesty-rule violations that are machine-checkable: `absent` rights carrying an
  instrument (the absence IS the fact), deprecations without a reason,
  object scopes off the `"<object>: <aspect>"` convention (warning)
- checksum/manifest drift (SHA256SUMS and counts must match the bytes)

`--strict` (release mode) also fails on warnings. Proof it works: the validator's
first-ever run caught a real integrity bug in our own `india-0.1.0` export —
`india-0.1.1` is the fix, and 0.1.0 stays published as the honest record.

## Layer 1 — provenance gates (review protocol)

What a machine can't check — whether a citation actually supports a row — the
review protocol does:

- A PR introducing or upgrading **`high`** rows must quote the operative
  provision text or link the authoritative source in the PR description.
  Reviewers check the *content*, so contributor identity never has to be trusted.
- Corrections to existing rows require a ledger entry
  (`ledgers/corrections.jsonl`: before/after/source/contributor) — silent edits
  to civic facts are the attack we defend against.
- Unreviewed contributions land at **`medium` at best** — the confidence cap.
  This mirrors the parent project's rule that made its dataset publishable:
  labeled uncertainty is data, unlabeled certainty is contamination.

## Layer 2 — adversarial & statistical scans (the truth pressure)

Structure being valid doesn't make it true. Truth pressure comes from:

- **Pivot falsifiability**: every dump names pivot places (`pivots.json`), and
  the analyzer's reports over them are concrete enough to be *wrong* in ways a
  local person notices ("that's not my constituency", "we're a Nagar Nigam, not
  a Palika" — both real catches from the pilot).
- **Contradiction tripwires**: run periodically and before release — duplicate
  offices per (nation, name); a place inside two divisions of the same
  exclusive kind (the constituency-bleed class); watchers nobody watches;
  offices with no constitutional path (the grounding gap is a report, not a
  shame — it's the to-do list).
- **Adversarial verification discipline**: claims are attacked with *retrieval*,
  not model votes. Pilot evidence, recorded in AGENTS.md: two grounded LLM
  verifiers refuted a true municipal fact and confirmed two mutually exclusive
  claims. LLMs propose; primary sources decide; verification fails CLOSED (an
  errored check is "unverified", never "confirmed").
- **Cross-registry checks** where official registries exist (India: LGD for
  divisions, ECI for constituencies): diffs are flagged for review — external
  registries are evidence, not oracles.

## Layer 3 — scoped authority & cryptographic accountability

- Merges need either a primary-source citation any maintainer can verify, or
  review by a **scoped authority** (AUTHORITIES.md) — expertise is earned
  per-domain ("forest law, IN-UK"), never global, and every vouch is recorded
  in ATTRIBUTIONS.jsonl, making it auditable and revocable.
- Signed commits; signed release tags; minisign over SHA256SUMS — a dump from
  any mirror verifies offline. Reputation attaches to keys over time, so
  pseudonymous experts accumulate exactly the same accountability as named ones.

## Layer 4 — versioned accountability (nothing is ever quietly fixed)

- Dumps are immutable; errors are fixed **forward** in a new version with a
  ledger trail. Downstream atlases pin versions, so a bad row can be traced to
  exactly the release that introduced it and the PR that merged it.
- **Release gate**: a version ships only when `validate.py --strict` is clean,
  the tripwire scan report is attached to the release notes, the pivot reports
  run, and the tag is signed. (This is the open-repo equivalent of the parent
  project's "dataset_qa must report 0 issues" pre-release rule.)

## What we deliberately do NOT claim

The dump asserts *sourced structure*, never conclusions. Rows are facts-with-
provenance; aggregate numbers (path counts, loop completeness) are descriptive
candidates. Analytical claims ("federal systems decentralize X") need their own
statistical guards (null models, cross-country replication) and belong in the
research layer of downstream projects, not in this dataset. Keeping that line
is itself a quality mechanism: it prevents the data from inheriting the
credibility of claims it hasn't earned.

## The life of an error (found → verified → fixed → propagated)

The pilot ran this end-to-end on a real error — our own curated seed said
Kotdwar was a Nagar Palika Parishad; it is a Nagar Nigam — so each step below
is exercised, not hypothetical.

**1. Found.** Four detection surfaces, in rising order of reach:
CI validation (structural breakage); `scan.py` tripwires (valid-but-suspicious
rows: duplicates, division bleed, unwatched watchers, grounding gaps, proxy
drift — a hit is a QUESTION, not a finding); pivot falsifiability (a local
person notices concrete wrongness and files the "Report an inaccuracy" issue —
no source required, local knowledge is exactly how the Kotdwar error surfaced);
and scheduled adversarial passes re-checking samples against primary sources —
including `high` rows, because LAW CHANGES: yesterday's verified fact is
tomorrow's stale row, so accuracy decays without re-verification.

**2. Verified.** Retrieval, not votes (the pilot's grounded LLM verifiers
refuted the true claim). Overturning an existing `high` row needs primary or
authoritative sources a maintainer can check, or a scoped authority's recorded
review. Verification fails closed: unresolved stays flagged, never "confirmed".

**3. Fixed — three mechanisms matched to three error types:**
- *Wrong value* → *correction*: row changed in the next dump version + a
  `ledgers/corrections.jsonl` entry (before / after / source / contributor).
- *Duplicate* → *merge*: links repointed to the survivor; merge recorded in the
  ledger. (Kotdwar had two synthetic mayor offices folded into the corrected one.)
- *Wrong existence* (fabricated office, misattributed power) → *deprecation,
  not deletion*: the row stays, flagged with a mandatory reason (validator-
  enforced), excluded from analysis — a public retraction, journal-style,
  because someone may have cited it. (Kotdwar's generic "sarpanch with
  policing power" went this way.)
Nothing is ever silently edited: the git diff, the ledger entry, and the
version bump make every fix itself auditable.

**4. Propagated.** The fix ships as a new immutable PATCH version with a signed
tag and a CHANGELOG entry naming the error; the Kaggle mirror updates with the
same version notes; downstream atlases (which pin dump versions) bump
deliberately and can render retraction notices on affected pages. Anyone who
cited the old version can diff exactly what changed and why — immutability is
what makes being wrong recoverable.

Current triage queue: `python scan.py dumps/india-0.1.1 --pivot kotdwar`
reports 16 open tripwire hits in non-pivot cities (division bleed in
Hyderabad/Araria/Coimbatore/Noida/Gurgaon, incl. Araria's dual municipal
identity — the same error class the pivot already went through). They are
listed, labeled, and awaiting retrieval-based verification — which is the
system behaving correctly: suspicion is cheap, correction is earned.
