# Current State

## Status

Active. Scope remains domestic DP3 TSP-to-Government read-only post-audit. M1
still has external public-source gaps, M2's public-source logical contract is
complete, M3 has nine published deterministic packages plus six conflict-
blocked draft rules, M4 has two monetary shadow-rating families, and M5 has one
charge-family reconciliation adapter inside a deterministic report envelope.

## Active milestone

M1 remains active for current PPA artifacts and disputed source versions. M3 and
M4 advance only where a source-complete charge exists. M5 is now the immediate
focus: Item 28A has end-to-end rating, audit reconciliation, and canonical
reporting; Item 28B has published rating but not invoice/payment reconciliation
or a report adapter. No authorized historical case is loaded.

## Last checkpoint

Published `2026.item-28b-extra-delivery.1` under Decision 0004 / `INT-0002`.
The evaluator uses actual pickup date, exact completed extra-delivery occurrences
before final delivery, timely Destination-PPSO authorization, reviewed evidence,
and exact `occurrences * 198.50 USD` arithmetic. Its 25 synthetic cases and five
result-tamper probes pass. `CF-0001` and `CF-0003` remain open broadly.

## Completed

- Ratified the domestic DP3 post-audit goal, 25-authorized-case completion
  verifier, and strict sensitive-data boundary.
- Archived/checksummed ten public artifacts. The physical registry holds 40
  reviewed claims, 37 locators, four open conflicts, and two approved scoped
  interpretations.
- Completed the public-source conceptual/logical schema and 11 synthetic logical
  scenarios with paired negative probes.
- Published seven immutable reference/workflow packages: initial weight,
  automatic reweigh, completed-reweigh selection, lower scale-weight selection,
  constructive weight, containerized provisional weight, and reweigh-refund
  workflow.
- Published Item 28A rating `2026.item-28a-extra-pickup.1` under `INT-0001` and
  Item 28B rating `2026.item-28b-extra-delivery.1` under `INT-0002`, both with
  exact Decimal arithmetic, source trace, and evidence gates.
- Implemented Item 28A exact expected/invoiced/paid reconciliation over immutable
  invoice, line, payment-allocation, and reviewed completeness history.
- Preserved the validated upstream Item 28A calculation and evidence trace in
  audit policy `2026-08-03.2` and registered `CHARGE-ADAPTER-DP3-ITEM-28A-V1`.
- Added deterministic explanations, stable finding order, source/evidence
  indexes, exact summary math, canonical JSON, and all-or-nothing report totals.
- Verified four synthetic Item 28A report paths, ten report-tamper probes, and
  three request-contract probes.

## Current task

Design the Item 28B post-audit contract: immutable corrected invoice/payment
facts, reviewed completeness and evidence gates, exact expected/invoiced/paid
variance, Item 28B-specific mapping under `INT-0002`, and a second registered
adapter for a real multi-family synthetic report.

## Known blockers

- `CF-0004`: the governing source does not identify the weight fact selecting
  the 5,000-lb reweigh-tolerance branch.
- Direct archival requests to PPA.mil and media.defense.gov returned HTTP 403.
- Mileage/SIT effective periods, authorized-SIT percentage/rounding, and the
  complete current domestic item-code supersession chain remain unresolved.
- `CF-0001` remains open outside the narrow Item 28B actual-pickup decision.
- `CF-0003` remains open outside approved Item 28A/28B row contracts; neither
  `INT-0001` nor `INT-0002` authorizes Item 28C or broader code-list use.
- Final acceptance requires at least 25 authorized, anonymized historical cases
  with independently approved outcomes.

## Decisions needed

- Resolve `CF-0004` before reweigh-fee or containerized-reimbursement tolerance.
- Resolve `CF-0001` before any other SIT/accessorial rate-date selection.
- Resolve `CF-0002` before disputed transit/SIT-tool behavior.
- Resolve `CF-0003` before broad 2022 item-code use.
- Reopen `INT-0001` or `INT-0002` if contrary or superseding evidence is
  archived.

## Next three actions

1. Add a synthetic immutable Item 28B invoice/payment history fixture with
   explicit `INT-0002` mapping and audit-completeness assertions.
2. Implement deterministic Item 28B post-audit reconciliation and boundary,
   missing/unsupported line, payment, evidence, chronology, and tamper cases.
3. Register and validate a second charge adapter, then exercise a two-family
   Item 28A + Item 28B canonical report without weakening all-or-nothing totals.

## Verification status

The registry contains ten public sources, 40 claims, 37 locators, four open
conflicts, two approved interpretations, ten packages, and 25 rules. Nine
packages and 19 rules are published; six rules remain draft. Passing suites:
registry valid plus nine expected failures; logical schema 11 positive plus 11
negative; initial weight 14; automatic reweigh 10; completed reweigh 11;
scale-reweigh lower 11; constructive reference 15; containerized provisional
15; reweigh-refund workflow 16; Item 28A rating 24 plus five tamper probes; Item
28A audit 27 plus seven tamper probes; audit report four plus ten output-tamper
and three request probes; Item 28B rating 25 plus five tamper probes; Item 28B
decision dossier four archived sources, ten mandatory tests, and four tamper
probes; source readiness seven candidates, 16 provenance records, five blockers,
and six tamper probes. Python compilation and `git diff --check` pass. No real
data, Item 28B audit adapter, live submission, money movement, or historical
acceptance report exists.
