# First Monetary Charge-Family Inventory

Status: reviewed source assessment; Item 28A was selected and published as the
first immutable package under Decision 0003 / `INT-0001`. Item 28B was
subsequently published under Decision 0004 / `INT-0002`; current sequencing is
maintained in `docs/monetary-source-readiness-matrix.json`.

Assessment date: 2026-08-03.

## Outcome

Item 28A's extra-pickup stop-off fee is approved as the first 2026
shadow-rating family under scoped Decision 0003 / `INT-0001`. Its arithmetic is
only:

`completed eligible extra-pickup occurrences × 198.50 USD per occurrence`

That expression is implemented with exact `Decimal` arithmetic. The current
authoritative tariff and rate workbook establish the service rule and numeric
rate. The archived 2022
listing supplies the remaining row-level contract, and the official public
library snapshot retrieved 2026-08-03 proves that the exact listing remained
published at the tariff's incorporated location. `INT-0001` approves that
combined evidence only for Item 28A during the 2026 rate cycle. `CF-0003`
remains open for the listing as a whole.

## Source basis

| Source | Version and effective period | Locator | Retrieved | Interpretation used here |
|---|---|---|---|---|
| `SRC-DP3-2026-400NG` | Published 2025-12-05; effective 2026-05-15 through 2027-05-14 | Item 1.2(c), p. 18; Item 4, pp. 19-20; Item 28, pp. 35-37; Item 50, p. 42; Item 105, pp. 44-49; Item 120, pp. 49-52; Item 130, pp. 54-55 | 2026-08-03 | Reviewed governing text |
| `SRC-DP3-2026-RATES` | Version 2026; effective 2026-05-15 through 2027-05-14 | `Additional Rates!A1`; candidate cells `A3:F3`, `A13:F13`, `A15:H52` | 2026-08-03 | Numeric cells and headings reviewed; package remains disputed where rate-date selection depends on `CF-0001` or `CF-0003` |
| `SRC-DP3-ITEM-CODES` | Published 2022-08-12; effective and supersession periods unstated | `DOM_400NG!A4:Q149`; candidate rows 8-9, 23-26, 32-48, and 53-118; legends `B154:L166` | 2026-08-03 | Direct workbook values reviewed; row 23 is approved only for 2026 Item 28A by `INT-0001` and row 24 only for 2026 Item 28B by `INT-0002`; every other use remains disputed under `CF-0003` |

The raw artifacts and hashes remain registered in
`sources/source-manifest.csv`. Workbook extracts were produced read-only by
`scripts/inspect_archived_workbooks.py` and are recorded in
`sources/derived/2026/workbook-structure.json`; no raw source was modified.

## Candidate comparison

| Priority | Narrow family | Rate and unit evidence | Rule and evidence requirements | Exact blocker or reason to defer |
|---|---|---|---|---|
| 1 | Item 28A extra-pickup stop-off fee | `Additional Rates!A13:F13`: 198.50 USD, per occurrence, shared by 28A/28B/28C. The 2022 listing row 23 says `EA`. | Item 28.1 and 28.3: no fee when the only pickup/delivery is a self-storage or mini-warehouse; each additional pickup after the first must be Government-requested through pre-approval or BL block 13 and actually performed. Required facts are original pickup, ordered stop, performed stop, location kind, and authorization evidence. | Source gate satisfied only by Decision 0003 / `INT-0001`. Implement with the approved 2026 scope and mandatory regression tests; do not generalize to 28B/28C or other listing rows. |
| 2 | Item 4 reweigh fee | `Additional Rates!A3:E3`: 125.00 USD. Item 4.4 requires billing through 226A with the note `reweigh fee`, not through 4A/4B, and disallows discount. | Item 4.5 makes payment conditional on initial-versus-reweigh results and tolerance. Existing reviewed ticket and workflow evidence can support the observations. | `CF-0004` leaves the weight fact selecting the 5,000-lb tolerance branch unstated. `CF-0003` also leaves the current 226A/4A/4B billing contract unresolved. |
| 3 | Item 130 light/bulky fee | `Additional Rates!A52:E52`: 297.78 USD. The 2022 listing rows 53-118 say `EA` for 130A-130J. | Item 130 requires pre-approval, an expressly listed eligible article, exclusions for Code 2/crating and one-person standard-carton handling, and service-performance evidence. | `CF-0003` controls the current `EA`, actual-pickup-date, service-location, and approval contract. Article classification and one-charge-per-combined-service quantity also require a larger fact model than Item 28A. |
| 4 | Item 120 extra labor | `Additional Rates!A44:E51`: schedule-specific regular and overtime hourly rates. The 2022 listing rows 37-48 say `TH`. | Item 120 requires Government request/pre-approval, service not included elsewhere, worker count, service location, start/end facts, regular/OT classification, and Item 22 fractional-hour treatment. | `CF-0003` controls current date basis, unit, schedule reference, and approval contract. Schedule selection and regular/OT boundary splitting make this a later family even after closure. |
| 5 | Item 105B regular crating | `Additional Rates!A31:E34`: 42.99 USD per cubic foot in every displayed schedule. | Item 105 requires approval, eligible new crating, actual and compensation-capped dimensions, four-cubic-foot minimum, Code 2/Code D treatment, and retained dimension evidence. Cubic dimensions are truncated to two decimal places. | `CF-0003` controls the current `CF` billing unit and approval contract. The text also needs an approved interpretation of how “per each cu. ft. or fraction thereof” interacts with invoicing a two-decimal truncated volume before money is published. |
| 6 | Item 105A full pack/unpack | `Additional Rates!A15:H30`: schedule and weight-band pack rates plus displayed unpack values. | Item 105 requires adjusted net weight, origin/destination schedules, performed/waived services, vehicle-weight deductions, and the TSP linehaul discount. | In addition to `CF-0003`, the family needs a TSP-specific discount input and verified order of operations/rounding. It is not the narrowest first monetary rule. |

SIT, SIT pickup/delivery, linehaul, and shorthaul were not promoted as first
candidates. They depend on mileage, weight bands, discounts, or the unresolved
SIT/accessorial date and transit issues in `CF-0001` and `CF-0002`.

## Satisfied source gate for Item 28A

The third gate originally identified by this inventory is satisfied. The
project owner approved Decision 0003 / `INT-0001` after the official library
page was archived and checksummed. The decision independently establishes the
2026 Item 28A rate-date basis, `EA` unit, location fields, and approval behavior
without approving the complete 2022 listing.

The published package now covers zero, one, and multiple additional pickups;
the self-storage-only exclusion; missing or unreviewed authorization and
performance evidence; ordered-but-not-performed stops; duplicate occurrences,
approvals, and evidence; both rate-cycle boundaries; exact-decimal
multiplication; and result/provenance tampering. Monetary output identifies the
exact rate cell and source versions and exposes every counted occurrence and its
reviewed evidence.
