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
- open conflict cases, scoped interpretation decisions, and their affected rule
  candidates; and
- a draft rule package whose disputed rules are blocked from publication; and
- a separate published initial-weight reference package sourced from reviewed
  400NG Item 4 claims; and
- a separate published Item 4.8 automatic-reweigh requirement package; and
- a separate published lowest-current-completed-reweigh selection package with
  reviewed ticket and DPS-update evidence gates; and
- a separate published lower-of-initial-and-completed-reweigh scale-reference
  package sourced only from the Tender's general lower-weight obligation; and
- a separate published constructive-weight calculation and selection package
  sourced from 400NG Item 4.11(e) and the DTR PPSO-approval gate; and
- a separate published containerized provisional-weight calculation and lower-
  selection package sourced only from 400NG Item 4.13(1)-(2); and
- a separate published post-invoice reweigh refund and billing-hold workflow
  package sourced from 400NG Item 4.12, Tender 8.a.(2)(d), and DTR D.7.b.; and
- a separate published Item 28A extra-pickup monetary package using the scoped
  source contract approved by Decision 0003 / `INT-0001`.

The CSV manifest remains the archival authority for issuer, title, version,
effective period, retrieval date, byte length, checksum, canonical URL, and
archive status. A registry source version joins to exactly one manifest row.

Run:

```text
python scripts/validate_source_rule_registry.py
```

The validator recomputes every raw artifact's byte length and SHA-256 digest,
checks source/locator/claim relationships, validates conflict evidence, requires
rule provenance and dependencies, validates the reviewer, scope, claims,
regression coverage, and reciprocal rule link for interpretation decisions, and
rejects publication through an open conflict. Test cases in
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

The completed-reweigh package selects the exact lowest net among current
completed reweigh observation versions. It does not compare that result with the
initial shipment weight, choose a controlling billed weight, apply CF-0004
tolerances, or produce a financial result.

The scale-reweigh lower-reference package compares verified results from the
initial and completed-reweigh packages. It intentionally does not use the
narrower within-tolerance claim, decide a charge-specific billed weight, or
produce a financial result.

The constructive-weight package preserves exact `cu_ft * 7 lb/cu_ft` arithmetic,
applies no unstated rounding, and selects the lower valid-ticket or constructive
candidate. It does not apply fees, reimbursement tolerances, refunds, billing
codes, or money.

The containerized provisional-weight package preserves exact `new gross -
original tare` arithmetic and selects the lower final initial or provisional
net. It deliberately ignores later new-tare completion facts and does not apply
the `CF-0004`-blocked reimbursement tolerance, fees, refunds, billing codes, or
money.

The reweigh-refund workflow package consumes only a verified lower-weight result
and immutable invoice/evidence events. It decides supplemental-refund necessity
and hold-release readiness without calculating the refund or applying any fee,
tolerance, billing-code, or payment logic.

The Item 28A package uses the original requested pickup date, immutable stop and
service events, reviewed Government-decision and completion evidence, and exact
`occurrence count * 198.50 USD` arithmetic. A blocked fact or evidence chain
emits no amount. Its approved item-code continuity cannot be reused outside the
2026 Item 28A scope.

Reviewed DTR Appendix A-A claims also register the observed-data basis for
line-item payment reporting, post-payment audit inputs, and line-item identity
matching. The deterministic comparison formulas remain a separately versioned
internal audit policy rather than being misrepresented as tariff rules.
