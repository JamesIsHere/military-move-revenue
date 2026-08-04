# Current State

## Status

Active. The ratified scope remains domestic DP3 TSP-to-government read-only
post-audit. M1 still has external public-source gaps, M2's public-source logical
contract is complete, M3 has eight published deterministic packages plus six
conflict-blocked drafts, and M4 has begun with the first monetary shadow-rating
package.

## Active milestone

M1 remains active for current PPA artifacts and disputed source versions. M3
continues as additional source-complete rules are found. M4 is in progress:
Item 28A now produces an evidence-bound exact expected charge, but no invoice or
payment comparison exists yet.

## Last checkpoint

Published immutable package `2026.item-28a-extra-pickup.1` under Decision 0003 /
`INT-0001`. It selects the rate version by original requested pickup date,
counts only completed extra pickups after the first with reviewed Origin-PPSO
decision and completion evidence, applies the self-storage-only exclusion, and
calculates `eligible occurrences * 198.50 USD` with exact `Decimal` arithmetic.
Blocked cases expose no amount or expected-line action. Twenty-four synthetic
cases and five result-contract tamper probes pass.

## Completed

- Ratified `goal.md`, including the 25-authorized-case historical completion
  verifier and strict sensitive-data boundary.
- Archived and checksummed ten public artifacts. Registered 34 reviewed claims,
  32 precise locators, four open conflicts, and one approved scoped
  interpretation.
- Completed the conceptual/logical public-source schema and nine synthetic
  logical scenarios with paired negative probes.
- Implemented the physical source/rule registry with artifact hash checks,
  immutable packages, source/locator/claim provenance, dependencies, evidence
  requirements, conflict publication gates, and interpretation-decision
  reciprocity.
- Published seven nonmonetary packages: initial weight, automatic reweigh,
  completed-reweigh selection, initial-versus-reweigh lower reference,
  constructive-weight reference, containerized provisional-weight reference,
  and reweigh-refund workflow.
- Inventoried six monetary candidates and recorded why the other five remain
  deferred by `CF-0003`, `CF-0004`, missing discount/order-of-operations facts,
  or larger service fact models.
- Archived the official USTRANSCOM DP3 public-library HTML (374,079 bytes,
  SHA-256 `0474F523B827DBEE09CC676AF3177AB6DC33E6F4DAB9640ADFEAE95BCC2150E5`)
  and verified line 4697 still links the exact 12 August 2022 Item Code Listing.
- Recorded Decision 0003 / `INT-0001`, approving only the 2026 Item 28A row
  contract while preserving `CF-0003` for every other row and broader use.
- Modeled immutable Item 28A stops, performances, approval events, reviewed
  evidence links, document versions, and the requested-pickup rate-date fact in
  synthetic fixture `SYNTH-LS-009`, without money in the logical fixture.
- Published `RP-DP3-2026-ITEM-28A-1` with source-contract, occurrence-
  eligibility, and exact expected-charge rules. Results expose inputs, counted
  performance IDs, approval IDs, reviewed evidence IDs, exact math, all six
  source claim/version/locator triples, and `INT-0001`.
- Verified rate-cycle dates before/on/inside/on/after the boundaries; zero, one,
  and two occurrences; `198.50 * 2 = 397.00`; self-storage-only and denied/not-
  performed exclusions; missing or unreviewed evidence; duplicate occurrence,
  approval, and evidence rejection; exact-string quantities; units; chronology;
  decision scope; and result package/source/rule/amount tampering.

## Current task

Commit the complete Decision 0003 source-closure and Item 28A implementation
checkpoint. Then build the narrowest end-to-end post-audit slice: immutable
synthetic invoiced and paid Item 28A line versions plus deterministic comparison
against the published expected-charge result, with unsupported, missing,
underbilled, overbilled, and correctly billed outcomes.

## Known blockers

- `CF-0004`: the source does not identify the weight fact selecting the
  5,000-lb reweigh-tolerance branch.
- Direct archival requests to PPA.mil and media.defense.gov returned HTTP 403.
- Mileage/SIT effective periods, authorized-SIT percentage/rounding, and the
  complete current domestic item-code supersession chain remain unresolved.
- `CF-0003` remains open outside the approved 2026 Item 28A row. `INT-0001`
  cannot authorize Item 28B/28C or another item-code row.
- Final acceptance requires at least 25 authorized, anonymized historical cases
  with independently approved outcomes.

## Decisions needed

- Resolve `CF-0004` before publishing reweigh-fee or containerized-
  reimbursement tolerance logic.
- Resolve `CF-0001` before SIT/accessorial rate-date selection.
- Resolve `CF-0002` before disputed transit/SIT-tool behavior.
- Resolve `CF-0003` before using the 2022 listing broadly.
- Reopen `INT-0001` if a contrary or superseding Item 28A source is archived.

## Next three actions

1. Add immutable synthetic invoice-line, payment-allocation, and version-history
   facts for Item 28A without changing the published rating package.
2. Implement a deterministic comparison that consumes a provenance-complete
   final Item 28A result and classifies missing, unsupported, underbilled,
   overbilled, correctly billed, and payment differences using exact decimals.
3. Add evidence, duplicate/version, blocked-upstream, amount/unit, and result-
   tampering tests; keep any ambiguous item-code matching in human review.

## Verification status

The registry contains ten public sources, 34 claims, 32 locators, four open
conflicts, one approved interpretation, nine packages, and 22 rules. Six rules
remain disputed drafts; 16 are published (13 prior reference/workflow rules and
three Item 28A rules). The registry validator passes its valid case and nine
expected failures. Passing suites: initial weight 14, automatic reweigh 10,
completed reweigh 11, scale-reweigh lower reference 11, constructive reference
15, containerized provisional 15, reweigh-refund workflow 16, Item 28A 24 plus
five tamper probes, and logical schema nine positive plus nine negative probes.
Python compilation and `git diff --check` pass. No expected-versus-invoiced-
versus-paid comparison, reconciliation disposition, live invoice submission, or
historical acceptance report exists yet.
