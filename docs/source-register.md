# Source Register

This is the human-readable intake queue and companion to the current
`sources/source-manifest.csv`. The manifest will be expanded or migrated when
the source metadata model is implemented.

Source precedence and conflict workflow are governed by
`docs/decisions/0002-source-precedence-and-conflicts.md`. Active interpretation
cases are preserved in `docs/conflict-register.md`.

## Status vocabulary

- `identified`: authoritative location known; artifact not archived.
- `archived`: raw artifact saved and checksummed.
- `extracting`: source-to-field or source-to-rule extraction underway.
- `reviewed`: extraction checked against the raw source.
- `implemented`: extracted concepts represented in schema/rules and tested.

## Authority classes

1. `governing`: binding tariff, tender, regulation, official amendment, or
   controlling direction.
2. `official-operational`: government form, system convention, code table,
   training, or procedural guide.
3. `adjudicative`: decision applying rules to a dispute.
4. `contractual-private`: authorized customer or compensation agreement.
5. `contextual`: vendor or industry explanation; never independently governing.

## P0 — required before logical schema freeze

| ID | Source | Class | Primary schema contribution | Status |
| --- | --- | --- | --- | --- |
| SRC-DP3-2026-400NG | [2026 Domestic 400NG](https://www.business.ustranscom.mil/dp3/docs/otherpdfs/0840%2B2026_Business_Rules/2026%20400NG%20%285%20Dec%2025%29%20Final.pdf) | governing | Charges, weights, reweighs, SIT, mileage, fuel, time, calculations, evidence references | archived; extracting (weight and SIT sections reviewed) |
| SRC-DP3-2026-RATES | [2026 400NG baseline rates](https://www.business.ustranscom.mil/dp3/pdfs.cfm) | governing | Rate-table keys, measures, geography, effective periods | archived; structurally reviewed; date-selection conflict open |
| SRC-DP3-2026-TOS-C1 | [2026 Tender of Service Change 1](https://www.business.ustranscom.mil/dp3/docs/otherpdfs/0840%2B2026_Business_Rules/2026%20Tender%20of%20Service%20Change%201%20%2818%20Feb%202026%29.pdf) | governing | Obligations, dates, events, evidence, actors, service performance | archived; extracting |
| SRC-DTR-IV-A402 | [DTR Part IV — Chapter A-402](https://www.business.ustranscom.mil/dtr/part-iv/dtr_part_iv_A_402.pdf) | governing | Shipment lifecycle, dates, locations, weights, SIT, approvals | archived; extracting (lifecycle/SIT reviewed) |
| SRC-DTR-IV-A413 | [DTR Part IV — Chapter A-413](https://www.business.ustranscom.mil/dtr/part-iv/dtr_part_iv_A_413.pdf) | governing | Bill-of-lading structure and responsibilities | archived; extracting |
| SRC-DTR-IV-AAA | [DTR Appendix A-A — TPPS](https://www.business.ustranscom.mil/dtr/part-iv/dtr_part_iv_app_A-A.pdf) | governing | BL/invoice cardinality, invoice lines, statuses, identifiers, submissions, acknowledgements, payments | archived; invoice-line matching, line payment data, and post-payment audit inputs reviewed; extracting remainder |
| SRC-FORM-DD619-2025 | [DD Form 619, February 2025](https://www.esd.whs.mil/Portals/54/Documents/DD/forms/dd/dd0619.pdf) | official-operational | Shipment parties, accessorial evidence, origin/destination, signatures and dates | identified; official server blocks archival request |
| SRC-DTEB-REFDATA | [DTEB reference data](https://www.business.ustranscom.mil/cmd/associated/dteb/reference-data.cfm) | official-operational | Controlled codes, definitions, value-set governance | identified |
| SRC-DP3-ITEM-CODES | [DP3 library — item-code listing](https://www.business.ustranscom.mil/dp3/pdfs.cfm) | official-operational | Billable-service and system item-code vocabulary | archived; structurally inspected; supersession unresolved |
| SRC-DP3-LIBRARY-SNAPSHOT-2026-08-03 | [DP3 public library snapshot](https://www.business.ustranscom.mil/dp3/pdfs.cfm) | official-operational | Reproducible publication-state evidence for the linked 12 August 2022 Item Code Listing | HTML archived and checksummed 2026-08-03; supports Item 28A-only `INT-0001` |
| SRC-DP3-MILEAGE-SIT | [DP3 library — mileage/transit/SIT tool](https://www.business.ustranscom.mil/dp3/pdfs.cfm) | official-operational | Distance, transit, ZIP/basing, SIT lookup inputs | archived; structurally inspected; effective date/transit conflict unresolved |
| SRC-DP3-2026-TRANSIT | [2026 transit-time tables](https://www.business.ustranscom.mil/dp3/pdfs.cfm) | official-operational | Origin/destination lookup dimensions and transit-day measures | archived; domestic sheet reviewed |
| SRC-DP3-2026-ADVISORIES | [DP3 advisories](https://www.business.ustranscom.mil/dp3/pdfs.cfm) | governing | Mid-cycle overrides and clarifications, including billing and fuel | identified |
| SRC-PPA-RESOURCE-CENTER | [PPA Industry & Government Resource Center](https://www.ppa.mil/Industry-Government-Resource-Center/) | official-operational | Current publication index, advisories, and operational quick links after the 2026 PPA website transition | identified; online text inspected 2026-08-03; raw HTML capture blocked by CDN |
| SRC-PPA-ADV-26-0105 | [PPA Advisory 26-0105 — official PPA website](https://media.defense.gov/2026/Jul/06/2003957897/-1/-1/0/DOW%20PPA%20PP%20ADVISORY%2026-0105%20PROMOTE%20THE%20OFFICIAL%20DOW%20PPA%20WEBSITE.PDF) | governing | Establishes the new PPA site as the authoritative current public resource surface | identified; online text inspected; raw PDF download blocked by CDN |

## P1 — required before external interchange or broad evidence automation

| ID | Source | Class | Primary schema contribution | Status |
| --- | --- | --- | --- | --- |
| SRC-DTEB-EDI859 | TPPS/DTEB EDI 859 convention or authorized implementation guide | official-operational | Exact invoice field types, lengths, loops, qualifiers, and conditional requirements | locate/access needed |
| SRC-DTEB-EDI997 | DTEB EDI 997 convention | official-operational | Syntax acknowledgement and rejection model | locate/access needed |
| SRC-DTEB-EDI824 | TPPS/DPS EDI 824 guidance | official-operational | Business-error model | locate/access needed |
| SRC-FORM-DD619-1 | Current DD Form 619-1 or embedded DTR representation | official-operational | Additional service/evidence fields | locate/access needed |
| SRC-WEIGHT-TICKET | Certified weight-ticket requirements and representative formats | governing/operational | Weight observations, scale identity, timestamps, vehicle facts, certification | locate/access needed |
| SRC-GSA-AUDIT | [GSA transportation invoice-audit guidance](https://www.gsa.gov/policy-regulations/policy/transportation-management-policy/transportation-invoice-audit) | official-operational | Audit terminology, comparison workflow, supporting-document principles | identified |

## P2 — interpretation and edge cases

| ID | Source | Class | Primary schema contribution | Status |
| --- | --- | --- | --- | --- |
| SRC-CBCA-RATE | Selected CBCA transportation rate decisions | adjudicative | Dispute facts, interpretations, adjustment and recovery patterns | identified |
| SRC-CBCA-1536-RELO-2009 | [CBCA 1536-RELO](https://www.cbca.gov/files/decisions/2009/DRUMMOND_10-01-09_1536-RELO__EVAN_F._MELTZER_508.pdf) | adjudicative | Certified-weight and supplemental-service evidence patterns; exact assessed-charge outcome | archived; complete three-page visual review; sanitized extract reviewed; out-of-scope context only |
| SRC-GAO-HHG | Selected GAO household-goods decisions | adjudicative | Historical interpretation and unusual fact patterns | identified |
| SRC-DP3-TRAINING | USTRANSCOM billing and business-rule training | official-operational | Worked examples and terminology | identified |
| SRC-DAYCOS-PUBLIC | Public Daycos workflow explanations | contextual | Operational vocabulary and user workflow hypotheses | identified |

## Explicitly deferred source families

- International Tender and international rate/control files.
- NTS Tender of Service and NTS contracts.
- DPM rules and TPPS formats specific to DPM.
- Claims and Liability Business Rules except where a billing source directly
  incorporates a required concept.
- Private agent compensation schedules.
- GSA civilian and commercial relocation tariffs.

## Extraction rule

No source moves to `reviewed` until its raw artifact is archived, hashed, and its
effective and supersession metadata are resolved. A source can inform a
provisional schema while `identified`, but the resulting fields must remain
provisional.

The archived workbooks were inspected on 2026-08-03 with an explicitly
user-authorized openpyxl read-only fallback after the artifact-tool runtime was
unavailable. Raw artifacts remain unchanged. The reproducible method, structural
extract, reviewed dimensions, and unresolved source conflicts are documented in
`docs/workbook-inspection.md` and
`sources/derived/2026/workbook-structure.json`.

Current-publication research, including the distinction between an archived
artifact and an unarchived online publication observation, is recorded in
`docs/source-currency-research.md`.
