# Current State

## Status

Active. The domestic DP3 TSP-to-government post-audit goal remains ratified.
M1 source closure is externally constrained, M2's logical contract is complete,
and M3 contains seven published deterministic reference/workflow packages, a
conflict-aware draft registry, a verified immutable reweigh-observation
contract, and a reviewed first-monetary-family inventory.

## Active milestone

M1 — Establish the source foundation remains active for current PPA and
source-version gaps. M3 — Implement the source and rule registry is advancing
from reviewed 400NG/Tender material. M4 monetary shadow rating has not started.

## Last checkpoint

This cold-resume snapshot adds a source-verified monetary-family inventory to
the reweigh implementation checkpoint. It selects Item 28A extra pickup as the
preferred first shadow-rating family but records that `CF-0003` blocks
publication because the only complete rate-date, unit, location, and approval
contract is the 12 August 2022 Item Code Listing with no established 2026
effective or supersession period. No calculation code or monetary output was
added.

## Completed

- Ratified the domestic DP3 post-audit goal and 25-case historical completion
  verifier; archived and checksummed nine public source artifacts.
- Recorded 91 discoveries, the conceptual/logical contract, Decision 0002, and
  the source-conflict workflow.
- Added the file-backed physical registry and validator with archive hash checks,
  provenance, dependencies, evidence requirements, and publication gates.
- Published and implemented `2026.weight-determination.1`; 14 synthetic initial
  weight/evidence cases pass.
- Published and implemented `2026.automatic-reweigh.1`; ten Item 4.8 threshold,
  blocked-input, and tampering cases pass.
- Rendered and visually verified the controlling-weight/refund passages on
  400NG pp. 19 and 22-23 and Tender printed p. 20; checked DTR A-402 section
  D.7.b for operational evidence.
- Added ten reviewed claims (`CLM-0023`-`CLM-0032`) for reweigh fee eligibility,
  lower-weight invoicing, constructive weight, refunds/billing holds,
  containerized provisional/correction paths, duplicate reweighs, and DPS/ticket
  evidence.
- Documented that the Tender's general lower-weight obligation and 400NG's
  narrower fee/workflow provisions are scoped and additive, not directly
  conflicting.
- Registered `CF-0004` for the unstated weight fact that selects the 5,000-lb
  reweigh-tolerance branch. Two affected tolerance rules remain draft and
  blocked; the general lower-weight model is not blocked.
- Modeled two completed reweighs as distinct immutable observations and a late
  correction as a new version of the same observation. Gross, tare, net, ticket
  document, evidence, DPS update, record time, provenance, and three aligned
  supersession histories are verified synthetically.
- Published and implemented `2026.completed-reweigh-selection.1`; eleven
  synthetic current-version, corrected-observation, evidence, exact-decimal,
  tie, malformed-input, and tampering cases pass.
- Published and implemented `2026.scale-reweigh-lower-reference.1`; eleven
  synthetic lower/higher/tie, exact-decimal, blocked-upstream, provenance, unit,
  package, and result-tampering cases pass.
- Registered reviewed DTR claim `CLM-0033` for constructive-weight eligibility
  and responsible-PPSO approval, then modeled verified cubic volume, immutable
  approval evidence, and resolved valid-ticket availability in `SYNTH-LS-006`.
- Published and implemented `2026.constructive-weight-reference.1`; fifteen
  exact-calculation, lower/tie, documented-unavailability, blocked-evidence,
  upstream, provenance, unit, reference, and tampering cases pass.
- Modeled `CLM-0027` original-tare/new-gross provisional inputs and the later
  `CLM-0028` new-tare completion as separate immutable ticketed observations in
  `SYNTH-LS-007`; reimbursement tolerance remains held by `CF-0004`.
- Published and implemented `2026.containerized-provisional-weight.1`; fifteen
  exact-subtraction, lower/tie, later-completion isolation, blocked-evidence,
  readiness, upstream, unit, chronology, provenance, and tampering cases pass.
- Modeled the post-invoice reweigh refund workflow in `SYNTH-LS-008`: the
  original approved invoice remains immutable, a separate supplemental refund
  identity is retained without an amount, and DPS update, PPSO ticket delivery,
  refund processing, and billing-hold release chronology are verified.
- Published and implemented `2026.reweigh-refund-workflow.1`; sixteen synthetic
  refund-required/not-required, hold-ready/not-ready, evidence, chronology,
  upstream-provenance, reference, and tampering cases pass with no money output.
- Inventoried six candidate monetary families against current 400NG rules,
  baseline-rate cells, units, rate-date selection, rounding, evidence, and open
  conflicts in `docs/monetary-charge-family-inventory.md`.
- Selected the 198.50 USD-per-occurrence Item 28A extra-pickup fee as the
  preferred first implementation after source closure; kept it unimplemented
  because `CF-0003` is material to the complete 2026 billing contract.

## Current task

Close `CF-0003` with a current authoritative domestic Item Code Listing, an
explicit continued-applicability/supersession record, or an approved scoped
interpretation. Once closed, register and implement the Item 28A extra-pickup
fee as the first monetary shadow-rating package with occurrence-level evidence
and exact-decimal tests.

## Known blockers

- CF-0004: the governing text does not identify the weight fact selecting the
  5,000-lb tolerance branch.
- Direct archival requests to PPA.mil and media.defense.gov returned HTTP 403.
- The mileage/SIT tool effective period, authorized-SIT percentage/rounding, and
  current domestic item-code supersession chain remain unresolved.
- Final acceptance requires at least 25 authorized, anonymized historical cases
  with independently approved outcomes.

## Decisions needed

- Resolve CF-0004 before publishing reweigh-fee or containerized-reimbursement
  tolerance logic.
- Resolve CF-0001 before SIT/accessorial rate-date selection.
- Resolve CF-0002 before the disputed transit/SIT-tool behavior.
- Resolve CF-0003 before treating the 2022 item-code workbook as authoritative
  for 2026.
- Approve Item 28A as the first monetary family only after `CF-0003` closure.

## Next three actions

1. Pursue an archivable current domestic item-code artifact or explicit
   continuation/supersession evidence that can close `CF-0003`.
2. If source retrieval remains constrained, prepare a scoped interpretation
   request for Item 28A covering rate-date basis, `EA` unit, location fields,
   and approval behavior without publishing a rule.
3. After approval, register and implement the Item 28A package with zero/one/
   multiple-occurrence, exclusion, authorization, rate-cycle, Decimal, and
   tampering tests.

## Verification status

The physical registry now contains 30 archived-source claims, 28 locators, four
open conflicts, eight packages, and nineteen rules: six disputed drafts and
thirteen published rules (four initial-weight, one automatic-reweigh, one
completed-reweigh selection, one scale-reweigh lower-reference, two
constructive-weight, two containerized-provisional, and two reweigh-refund
workflow rules). The registry
validator passes one valid case and seven expected failures. Initial weight (14
cases), automatic reweigh (10 cases), completed-reweigh selection (11 cases),
scale-reweigh lower reference (11 cases), constructive-weight reference (15
cases), containerized provisional weight (15 cases), reweigh refund workflow
(16 cases), and logical-schema
validation (eight positive scenarios and eight negative probes) pass. No
charge-specific billed-weight result, tolerance result, fee, refund amount,
billing item, expected invoice amount, or SIT result is implemented. Current
reweigh-observation, reference, containerized, and workflow work is included in
the current checkpoint.
