# Decision 0003 — Item 28A Scoped Item-Code Continuity

- Status: Accepted
- Date: 2026-08-03
- Approver: Project owner, by explicit session approval
- Scope: Domestic 400NG Item 28A extra-pickup shadow rating for the 2026 rate
  cycle only

## Context

The 12 August 2022 Item Code Listing has no stated effective or supersession
period. `CF-0003` therefore remains open for the listing as a whole. Item 28A is
narrower than that unresolved question:

- `SRC-DP3-2026-400NG`, published 2025-12-05 and effective
  2026-05-15 through 2027-05-14, names Item 28A in Item 28, pp. 35-36,
  establishes the extra-pickup eligibility conditions, and in Item 1.2(c), p.
  18, incorporates the official Item Code Listing for rate-date behavior.
- `SRC-DP3-2026-RATES`, version 2026 and effective 2026-05-15 through
  2027-05-14, names 28A at `Additional Rates!A13:F13` and supplies 198.50 USD
  per occurrence.
- `SRC-DP3-ITEM-CODES`, published 2022-08-12, supplies the Item 28A row at
  `DOM_400NG!A23:Q23`: requested-pickup date basis, `EA` unit, `SC` rate
  reference, `AB` additional-pickup location, Origin PPSO approval screen, and
  approval required.
- `SRC-DP3-LIBRARY-SNAPSHOT-2026-08-03`, retrieved 2026-08-03, archives the
  official USTRANSCOM public library HTML. Line 4697 still links the exact
  `Item Code Listing (12 Aug 2022).zip` artifact. The snapshot is 374,079 bytes
  with SHA-256
  `0474F523B827DBEE09CC676AF3177AB6DC33E6F4DAB9640ADFEAE95BCC2150E5`.

No contrary Item 28A source is archived. The newer PPA publication-location
observation remains candidate because its raw artifacts could not be archived.
It is therefore retained as a reason not to generalize this decision.

## Decision

For domestic 400NG Item 28A extra-pickup shadow rating only, the fields in the
12 August 2022 `DOM_400NG` row 23 are approved for use during the 2026 rate
cycle when combined with the current 2026 400NG eligibility text and the 2026
Baseline Rates value.

The approved contract is:

| Field | Approved value |
|---|---|
| Rate-version date fact | Original requested pickup date (`R`) |
| Billing item | `28A` |
| Unit | Each (`EA`) |
| Rate-basing reference | Point schedule (`SC`) |
| Required service location | Additional pickup (`AB`) |
| Approval screen | Origin PPSO |
| Approval required | Yes |

This decision is registered as `INT-0001` and authorizes only the following
three rules in the immutable 2026 Item 28A package:

- `RULE-ITEM-28A-SCOPED-SOURCE-CONTRACT`;
- `RULE-ITEM-28A-ELIGIBLE-OCCURRENCE`; and
- `RULE-ITEM-28A-EXPECTED-CHARGE`.

## Excluded scope

This decision does not:

- approve the complete 2022 item-code workbook for 2026;
- close `CF-0003` for any other item code or for broad invoice validation;
- approve Item 28B, Item 28C, SIT, or another accessorial family;
- establish applicability beyond 2027-05-14;
- authorize live invoice submission; or
- replace the need to reopen the interpretation if a contrary or superseding
  source is archived.

## Required implementation tests

The Item 28A package must cover:

- dates before, on, and after each 2026 rate-cycle boundary;
- zero, one, and multiple completed eligible extra-pickup occurrences;
- the self-storage-only exclusion;
- missing Government authorization and missing performance evidence;
- duplicated occurrences or evidence;
- exact-decimal multiplication; and
- rule, source, rate-cell, interpretation, and result tampering.

## Consequences

Item 28A advanced to deterministic implementation as immutable package
`2026.item-28a-extra-pickup.1` without treating `CF-0003` as globally resolved.
Every result cites the current tariff and rate cells, the archived item-code
row, the public-library snapshot, and `INT-0001`.
