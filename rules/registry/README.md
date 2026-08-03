# Physical Source and Rule Registry

This directory is the first physical registry increment for domestic DP3
post-audit. It deliberately uses version-controlled JSON plus the existing CSV
source manifest so the project can validate the domain contract before choosing
a database engine.

`registry.json` contains:

- immutable identities for archived source versions;
- precise locators and reviewed claims used by active conflict cases;
- candidate publication observations that are not promoted to archived source
  versions;
- open conflict cases and their affected rule candidates; and
- a draft rule package whose disputed rules are blocked from publication; and
- a separate published initial-weight reference package sourced from reviewed
  400NG Item 4 claims; and
- a separate published Item 4.8 automatic-reweigh requirement package.

The CSV manifest remains the archival authority for issuer, title, version,
effective period, retrieval date, byte length, checksum, canonical URL, and
archive status. A registry source version joins to exactly one manifest row.

Run:

```text
python scripts/validate_source_rule_registry.py
```

The validator recomputes every raw artifact's byte length and SHA-256 digest,
checks source/locator/claim relationships, validates conflict evidence, requires
rule provenance and dependencies, and rejects publication through an open
conflict. Test cases in
`tests/fixtures/source-rule-registry/registry-cases.json` exercise both the valid
draft registry and deliberately invalid publication/provenance mutations.

The published weight package determines initial net scale weight and evidence
sufficiency only. It does not calculate a fee, select a billing item code,
perform a reweigh decision, or rate a charge. A later increment may replace the
file-backed representation with database tables without weakening these
invariants.

The automatic-reweigh package determines only whether the stated grade-band and
weight thresholds require the TSP to perform a reweigh. It does not map raw
grades, apply reweigh-charge tolerances, or produce a billed service.
