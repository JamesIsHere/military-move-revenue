# Archived Workbook Inspection

## Method and scope

The four public P0 workbook families were inspected on 2026-08-03 using Python
3.14 and openpyxl 3.1.5 after the user explicitly authorized a read-only fallback.
The approved artifact-tool runtime was unavailable. ZIP members were read into
memory; no workbook was saved or recalculated. Formula text and stored cached
values were captured separately, numeric values were serialized lexically, and
all raw artifact hashes were checked against `sources/source-manifest.csv`.

The reproducible inspector is `scripts/inspect_archived_workbooks.py`. Its
structured output is `sources/derived/2026/workbook-structure.json`. No workbook
rendering engine was available, so this review covers workbook structure, cells,
styles, formula text, and cached values rather than visual page rendering.

## Inventory

| Source ID | Workbook | Sheets | Formula cells | In-scope contribution | Review status |
|---|---|---:|---:|---|---|
| `SRC-DP3-2026-RATES` | `400NG Baseline Rates.xlsx` inside the archived ZIP | 6 visible | 1 change-log external-link formula | ZIP3/BPC/service-area mapping; linehaul, SIT, and accessorial rate dimensions | Structurally reviewed; effective-date conflict open |
| `SRC-DP3-2026-TRANSIT` | 2026 transit-time workbook inside the archived ZIP | 13 visible | 4,488, all on international formula-bearing sheets | `Appendix L-Domestic` distance/weight/day matrix | Domestic sheet reviewed; international sheets out of scope |
| `SRC-DP3-ITEM-CODES` | 12 August 2022 item-code workbook inside the archived ZIP | 5 visible | 0 | Domestic billing-code, unit, location, date-basis, and approval vocabulary | Structurally reviewed; supersession/effective period unresolved |
| `SRC-DP3-MILEAGE-SIT` | Direct XLSX | 1 visible, 8 hidden | 24 | ZIP3 mileage lookup, transit bracket, and provisional authorized-SIT-day formula | Structurally reviewed; effective period and transit conflict unresolved |

## Baseline rates

The workbook is predominantly static reference data:

- `Base Point City!A1:E786` maps BPC, county, state, service area, and included
  ZIP3 values. Its note says two-digit ZIP3/service-area values have an unseen
  leading zero, so these identifiers must be stored as zero-padded text.
- `Geographical Schedule!A1:H229` maps service area number/name to service
  schedule, linehaul factor per cwt, Items 135A/B per cwt, Item 185A per cwt,
  Item 185B per cwt/day, and SIT pickup/delivery schedule.
- `Linehaul!B2:CU91` and `Accessorials!C2:CU101` use explicit lower/upper weight
  bands. The accessorial matrix contains 210A and 210D amounts by SIT schedule
  and weight band.
- `Additional Rates!A57:E64` contains 210B and 210E amounts by schedule. Item
  210B therefore combines a matrix-derived 210A amount with a schedule scalar,
  consistent with 400NG Item 210.

Every relevant rate sheet displays an effective date of 15 May 2026 followed by
“Based on Original Requested Pickup Date.” This conflicts with 400NG Item
1.2(c), page 18, which expressly selects tables in effect on actual pickup date
for SIT and listed accessorial services. Both claims remain recorded; no
effective-date rule is approved from the workbook banner alone.

## Domestic transit times

`Appendix L-Domestic!A1:F33` is a two-dimensional lookup:

- distance bands: 1–250 through 6,751–7,000 miles;
- weight bands: 1–999, 1,000–1,999, 2,000–3,999, 4,000–7,999, and 8,000+ lbs;
- result: transit days;
- Alaska adjustments: add 5 or 16 days depending on the Alaska destination
  grouping stated in rows 31–33.

The other twelve sheets are international or special-solicitation tables and
are outside the ratified domestic v1 boundary.

## Domestic item codes

`DOM_400NG!A4:Q149` supplies a versioned billing vocabulary rather than rate
amounts. Its columns identify requested/actual date basis, service code, fuel
surcharge treatment, discount family, origin/destination role, description,
two units, rate-basing reference codes, required location pairs and N101 codes,
L713 unit requirement, notes, approval screen, and approval requirement. Rows
154–166 define the code legends.

SIT rows establish, among other things:

- 185A uses billed weight and requires the DPS SIT control number in N9 with
  `N901=1R` and `N902=<control number>`;
- 185B uses days plus billed weight;
- 210A–210F use a flat-rate quantity, miles, explicit origin/destination
  location pairs, and measurement/billed-weight MEA segments;
- 210C/210F switch to the transportation discount family for over-50-mile
  treatment;
- 226A is a miscellaneous flat-rate line requiring the performed-service type
  in L502; and
- every cited SIT row is marked as requiring approval in the workbook.

Because the archived listing is dated 12 August 2022 and gives no effective or
supersession period, these controlled values remain provisional until a current
authoritative version or explicit continued applicability is established.

## Mileage, transit, and SIT tool

The visible `MAIN!C2:H13` sheet accepts weight and origin/destination ZIP3 values
and returns miles, transit time, and an “Auth SIT Day” result. Hidden sheets show
the implementation:

- `TREF!A1:C909` maps ZIP3 to a table code and one of four mileage sheets;
- `EREF!A2:B5` selects the applicable compressed mileage matrix;
- hidden sheets `A`–`D` contain the table-code mileage matrices;
- `WORK!I3` rounds mileage upward to a 250-mile transit bracket;
- `WORK!C5` selects one of five weight bands;
- `WORK!I4` looks up transit days from `TT!A1:F21`; and
- `WORK!I5` applies Excel `ROUND(transit_days * 0.7, 0)` for the displayed
  authorized-SIT-day result.

The tool states that it is for non-Alaska domestic direct-delivery shipments and
returns `DTOD` when both ZIP3 values are within the same base-point location.
Its archived `docProps/core.xml` identifies creator `SDDC`, last modifier
`Stroot, Sheldon CTR USTRANSCOM J6`, creation timestamp
`2009-06-12T18:38:05Z`, and modification timestamp
`2025-09-26T06:57:51Z`. This is embedded file metadata, not a publisher-stated
effective period, but it supplies a reproducible artifact-version marker and
shows the workbook predates publication of the 2026 transit table. Five stored
cached formula errors occur in nonselected mileage branches or the blank-weight
sample path; the selected sample mileage still has a cached result.

The hidden `TT` table conflicts materially with the archived 2026 domestic
transit table. For a synthetic 873-mile, 6,000-lb lookup, `TT!A5:E5` yields 9
days, while `Appendix L-Domestic!A5:E5` yields 18 days. The tool has no
publisher-stated version/effective date. The PPA resource center still links a
same-titled tool as a current quick-access resource on 2026-08-03, but the PPA
copy could not be downloaded through the CDN and therefore cannot yet be shown
to be byte-identical to this archived workbook. Neither publication presence nor
embedded modification time makes the hidden transit table or 70-percent formula
governing. The tool must not supply an approved transit or SIT entitlement rule
until the conflict is resolved.

## Schema consequences

- ZIP3, BPC, service area, item code, unit code, and location code are versioned
  controlled identifiers, not free text or database primary keys.
- Rate tables require explicit dimensions, inclusive boundaries, units, source
  cell locators, and effective-date decisions.
- Billing item codes require their own versions because service performance,
  tariff item, billed code, locations, units, and approvals are distinct.
- Spreadsheet formulas are source expressions to extract and test; published
  deterministic code must perform calculations and expose the selected source
  version, inputs, and interpretation.
- Conflicting workbook and tariff claims remain separate interpretation records
  until approved; neither is overwritten.
