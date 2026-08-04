# Current State

## Status

Active. Scope remains domestic DP3 TSP-to-Government read-only post-audit. M1
still has external public-source gaps, M2's public-source logical contract is
complete, M3 has eight published deterministic rule packages plus six conflict-
blocked drafts, M4 has one monetary shadow-rating family, and M5 now has its
first expected/invoiced/paid audit slice.

## Active milestone

M1 remains active for current PPA artifacts and disputed source versions. M3 and
M4 advance only where a source-complete charge exists. M5 is in progress: Item
28A can now be rated and reconciled through immutable synthetic invoice/payment
history, but no second charge family, batch audit envelope, or authorized
historical case is implemented.

## Last checkpoint

Implemented internal policy `AUDIT-DP3-ITEM-28A-RECONCILIATION-V1` version
`2026-08-03.1` and deterministic evaluator `rules/item_28a_post_audit.py`. It
validates the complete published Item 28A result, selects current invoice, line,
and payment-allocation versions, requires reviewed evidence and separate history-
completeness assertions through the audit cutoff, and emits exact billing,
payment, realized, and quantity variances. Twenty-seven synthetic audit cases
and seven output-tamper probes pass.

## Completed

- Ratified the domestic DP3 post-audit goal, 25-authorized-case completion
  verifier, and strict sensitive-data boundary.
- Archived/checksummed ten public artifacts. The physical registry now holds 37
  reviewed claims, 34 locators, four open conflicts, and one approved scoped
  interpretation.
- Completed the public-source conceptual/logical schema and ten synthetic
  logical scenarios with paired negative probes.
- Implemented immutable source/rule packages and publication validation for
  initial weight, automatic reweigh, completed-reweigh selection, lower scale-
  weight selection, constructive weight, containerized provisional weight,
  reweigh-refund workflow, and Item 28A monetary rating.
- Published `2026.item-28a-extra-pickup.1` under Decision 0003 / `INT-0001`.
  It calculates exact `eligible occurrences * 198.50 USD` and blocks missing or
  conflicting approval/performance evidence.
- Registered reviewed DTR Appendix A-A claims `CLM-0038`–`CLM-0040` for actual
  line-item payment data, post-payment audit inputs/supporting documents, and
  TPPS/DPS line-item identity matching.
- Documented the internal Item 28A audit policy separately from Government
  billing rules, with source ID, version, effective period, locators, retrieval
  date, and interpretation status.
- Modeled `SYNTH-LS-010`: corrected immutable invoice and line versions,
  remittance/payment allocation evidence, and reviewed invoice/payment history
  completeness through the audit cutoff.
- Implemented current-version validation, one-to-one accepted `28A`/`EA`
  matching under `INT-0001`, exact invoice totals, balanced current allocations,
  and full upstream package/provenance validation.
- Implemented billing findings `CORRECTLY_BILLED`, `MISSING_EXPECTED_CHARGE`,
  `UNSUPPORTED_BILLED_CHARGE`, `UNDERBILLED`, `OVERBILLED`, and
  `NO_CHARGE_EXPECTED_OR_BILLED`; separate quantity and payment findings; and
  open/closed disposition.
- Proved that absent history is never zero without reviewed completeness. Stale
  assertions, ambiguous/multiple matches, wrong interpretation, missing evidence,
  or blocked upstream rating produce `AUDIT_BLOCKED`, require human review, and
  expose no authoritative comparison.
- Verified corrected invoice and allocation histories, exact positive/negative
  variances, missing/unsupported charges, unpaid/partial/overpayment, quantity
  mismatch, currency/Decimal boundaries, totals, chronology, duplicates,
  supersession, evidence, and result tampering.

## Current task

Add a deterministic explanation and audit-report envelope that renders sources,
evidence, expected math, invoiced/paid comparison, finding codes, and blockers
without AI-authored financial conclusions. Design it as a reusable charge-
adapter contract so future source-complete families can join the same audit run.

## Known blockers

- `CF-0004`: the governing source does not identify the weight fact selecting
  the 5,000-lb reweigh-tolerance branch.
- Direct archival requests to PPA.mil and media.defense.gov returned HTTP 403.
- Mileage/SIT effective periods, authorized-SIT percentage/rounding, and the
  complete current domestic item-code supersession chain remain unresolved.
- `CF-0003` remains open outside approved 2026 Item 28A scope. `INT-0001`
  cannot authorize Item 28B/28C or another listing row.
- Final acceptance requires at least 25 authorized, anonymized historical cases
  with independently approved outcomes.

## Decisions needed

- Resolve `CF-0004` before reweigh-fee or containerized-reimbursement tolerance.
- Resolve `CF-0001` before SIT/accessorial rate-date selection.
- Resolve `CF-0002` before disputed transit/SIT-tool behavior.
- Resolve `CF-0003` before broad 2022 item-code use.
- Reopen `INT-0001` if contrary or superseding Item 28A evidence is archived.

## Next three actions

1. Define a versioned audit-result envelope and deterministic plain-language
   explanation contract for final and blocked findings.
2. Add a generic charge-adapter boundary that verifies an immutable upstream
   result before reconciliation while keeping Item 28A behavior unchanged.
3. Add report serialization, multi-finding ordering, explanation/source/evidence
   tamper tests, and a CLI-like synthetic audit-run fixture before pursuing the
   next source-blocked monetary family.

## Verification status

The registry contains ten public sources, 37 claims, 34 locators, four open
conflicts, one approved interpretation, nine packages, and 22 rules. Six rules
remain disputed drafts; 16 are published. Passing suites: registry valid plus
nine expected failures; logical schema ten positive plus ten negative; initial
weight 14; automatic reweigh 10; completed reweigh 11; scale-reweigh lower 11;
constructive reference 15; containerized provisional 15; reweigh-refund workflow
16; Item 28A rating 24 plus five tamper probes; Item 28A audit 27 plus seven
tamper probes. Python compilation and `git diff --check` pass. No real data,
batch audit report, second monetary family, live submission, money movement, or
historical acceptance report exists yet.
