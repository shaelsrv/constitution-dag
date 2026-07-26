# Contributing — collaboration, attribution, and trust

The premise of this repo: **the map is always incomplete, and the people who can
complete it are distributed** — a forest officer knows the Forest Act's real
teeth; a municipal clerk knows which committee actually signs; a election
official knows where the boundary files live. This document is the contract that
lets that knowledge flow in without degrading trust in the data.

Why it matters: a government citizens can *navigate* is a government citizens can
*hold to account*. Every verified row makes the black box a little more legible.

**Ways to help, from an afternoon to a standing role:**

- **Improve data** — fix an inaccuracy, add a task flow, deepen an office.
- **Add verified sources** — attach a primary-source reference that upgrades a
  claim from *estimated* (`medium`) to *earned* (`high`).
- **Contribute code** — improve `dag.py`, the validator, the viewer, exporters.
- **Review contributions** — vouch for others' PRs under the signing scheme.
- **Host a server** — run an instance for your region.
- **Become a country maintainer** — own a nation's map and shepherd its growth
  (`AUTHORITIES.md` lists maintainer keys and scopes).

## What a contribution looks like

All contributions are pull requests against a dump (or a new dump). Three kinds:

1. **Corrections** — a row is wrong (our pilot's own curated seed misclassified
   the pilot town's municipal status; a web source settled it). PR must cite the
   primary source and append a line to the dump's `ledgers/corrections.jsonl`:
   `{row, before, after, source_url, contributor, date}`.
2. **Enrichment** — new instruments, edges, scoped objects, rights, places.
   Every new row carries `source` + `confidence` per the honesty rules.
   `confidence: high` requires the provision text to be quoted or linked in the
   PR description; otherwise land it as `medium` — labeled uncertainty is
   welcome, unlabeled certainty is not.
3. **New countries** — a fresh `dumps/<country>-0.1.0/` following AGENTS.md.
   Seed-level is enough to publish; the version number says how mature it is.

### The domain-expert path (the forest-department case)

If you work inside a system this repo maps, you are exactly who we want, and
your contribution is handled with extra care in both directions:

- You contribute **structure and law** (offices, provisions, control edges,
  scope splits, how things actually route), never internal, personal, or
  non-public information. If it isn't in a gazette, statute, court record, or
  official publication, it doesn't belong in the dump — put the *pointer* to
  the public record in, not the private knowledge.
- Your expertise is declared in the PR ("I serve in the Uttarakhand forest
  department; ss. 52–68 practice notes below") and recorded in the attribution
  ledger — pseudonyms are fine (see identity below); we verify the *content*
  against public sources, so your claims never rest on your identity alone.
- Domain experts who sustain quality contributions get listed in
  `AUTHORITIES.md` with a scope ("forest law, IN-UK") and become preferred
  reviewers for that scope — authority is earned per-domain, never global.

## Attribution

- `ATTRIBUTIONS.jsonl` at the repo root records every merged contribution:
  `{contributor, scope, rows_added, rows_corrected, dump_version, date, pr}`.
- The data license is CC-BY 4.0: downstream users must credit
  "My Citizen Atlas contributors"; per-row blame is reconstructible from git
  history + the attribution ledger.
- Contributors choose their attribution name (legal name, handle, or
  pseudonym). What matters for trust is the key, not the name.

## Cryptographic trust (keys, not vibes)

The threat model is real for civic data: a hostile edit that quietly reroutes
"who controls the police" is worse than no data. Three layers, all standard
tooling:

1. **Signed commits.** Contributors sign commits (SSH or GPG signing — GitHub
   verifies both). A contributor's key IS their identity across time;
   pseudonymous keys build reputation exactly like named ones.
2. **Signed releases.** Every published dump version is git-tagged; the tag is
   signed by a maintainer, and `SHA256SUMS` inside the dump is additionally
   signed (`SHA256SUMS.minisig`, minisign) so a dump downloaded from ANYWHERE
   (Kaggle, a mirror, a torrent, a USB stick in a censored network) is
   verifiable offline against the maintainer public keys in `AUTHORITIES.md`.
3. **Scoped authorities.** `AUTHORITIES.md` lists maintainer keys and
   domain-expert reviewer keys with their scopes. Merges into a scope need
   either a primary-source citation any maintainer can check, or a review by a
   listed authority for that scope — and an authority's review is recorded in
   the ledger, so their vouching is itself auditable and revocable.

Nothing here requires trusting a server: the repo, the signatures, and the
dumps are all verifiable offline. (This mirrors the parent project's
self-hosting stance: censorship resilience is a design requirement, not a
feature.)

## Review gates (what maintainers check before merge)

1. Provenance: every new/changed row has `source` + `confidence`; `high` has
   the provision quoted or linked.
2. Honesty rules: checks not mixed into grants; objects as scopes not nodes;
   body-proxy convention on chamber powers; absences recorded, not skipped.
3. No PII, no non-public information, no personal data of any kind. Offices
   and current *public* officeholders only.
4. Ledger entries present for corrections/deprecations.
5. `python dag.py <dump> paths <pivot>` runs clean; SHA256SUMS regenerated.

## Integration back into nation-level atlases

This repo is the commons. Downstream instruments (nationAtlas and anything
else) sync from published dump versions — never from unreviewed branches. The
flow is one-way per release: contribute here → versioned, signed release →
atlases ingest with the version pinned. That keeps every atlas's provenance
chain anchored to a citable, immutable dump.
