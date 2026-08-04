# Current State

## Status

Active. Scope remains domestic DP3 TSP-to-Government read-only post-audit. M1
still has external public-source gaps, M2's public-source logical contract is
complete, M3 has eight published deterministic rule packages plus six conflict-
blocked drafts, M4 has one monetary shadow-rating family, and M5 now has one
expected/invoiced/paid charge adapter inside a deterministic report envelope.

## Active milestone

M1 remains active for current PPA artifacts and disputed source versions. M3 and
M4 advance only where a source-complete charge exists. M5 is in progress: Item
28A can be rated, reconciled through immutable invoice/payment history, and
rendered as a canonical source/evidence-backed report. No second charge family,
multi-family shipment report, or authorized historical case is implemented.

## Last checkpoint

The owner selected Decision 0004 Alternative A. Registered approved `INT-0002`,
three reviewed Item 28B claims, three locators, and immutable draft package
`2026.item-28b-extra-delivery.draft.1` with three rules, seven dependencies, and
three evidence gates. All Item 28B rules remain not implemented and unpublished;
`CF-0001` and `CF-0003` remain open broadly.

## Completed

- Ratified the domestic DP3 post-audit goal, 25-authorized-case completion
  verifier, and strict sensitive-data boundary.
- Archived/checksummed ten public artifacts. The physical registry holds 37
  reviewed claims, 34 locators, four open conflicts, and one approved scoped
  interpretation.
- Completed the public-source conceptual/logical schema and ten synthetic
  logical scenarios with paired negative probes.
- Implemented immutable source/rule packages and publication validation for
  initial weight, automatic reweigh, completed-reweigh selection, lower scale-
  weight selection, constructive weight, containerized provisional weight,
  reweigh-refund workflow, and Item 28A monetary rating.
- Published `2026.item-28a-extra-pickup.1` under Decision 0003 / `INT-0001` with
  exact `eligible occurrences * 198.50 USD` rating and evidence gates.
- Implemented Item 28A exact expected/invoiced/paid reconciliation with current
  immutable invoice, line, payment-allocation, and reviewed completeness
  history; ambiguous or incomplete inputs block without authoritative money.
- Preserved the complete validated upstream Item 28A calculation and reviewed
  evidence trace in audit policy version `2026-08-03.2`.
- Added a registry-style charge-adapter contract with immutable ID, version,
  family, audit policy, evaluator, and validator. Duplicate families, unknown
  adapters, cutoff mismatch, and data-status relabeling are rejected.
- Added deterministic billing, quantity, payment, and blocker explanations;
  stable finding ordering; source/evidence indexes; exact Decimal summary math;
  and canonical JSON serialization.
- Enforced all-or-nothing report totals: any blocked charge suppresses aggregate
  money and enters human review; decided open exceptions retain charge-level
  comparisons.
- Verified four synthetic report paths (closed, open exception, data blocked,
  upstream blocked), ten output-tamper probes, and three request-contract probes.

## Current task

Implement deterministic Item 28B rating under `INT-0002` with actual-pickup
date selection, completed additional deliveries before final delivery, reviewed
Government authorization/completion evidence, exact Decimal multiplication, and
all ten mandatory boundary/evidence/tamper test classes. Publish only after the
complete suite passes.

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

1. Add a synthetic Item 28B logical fixture and deterministic rating evaluator.
2. Add boundary, eligibility, authorization-channel, evidence, duplicate,
   Decimal, and result-tamper tests; publish a new immutable package version.
3. Add Item 28B invoice/payment reconciliation and a second report adapter only
   after the rating result contract is published.

## Verification status

The registry contains ten public sources, 40 claims, 38 locators, four open
conflicts, two approved interpretations, ten packages, and 25 rules. Nine rules
remain draft; 16 are published. Passing suites: registry valid plus
nine expected failures; logical schema ten positive plus ten negative; initial
weight 14; automatic reweigh 10; completed reweigh 11; scale-reweigh lower 11;
constructive reference 15; containerized provisional 15; reweigh-refund workflow
16; Item 28A rating 24 plus five tamper probes; Item 28A audit 27 plus seven
tamper probes; audit report four plus ten output-tamper and three request probes.
Python compilation and `git diff --check` pass. No real data, second monetary
family, multi-family report, live submission, money movement, or historical
acceptance report exists.

The source-readiness suite additionally passes seven candidates, 16 provenance
records, five blockers, and six tamper probes.
