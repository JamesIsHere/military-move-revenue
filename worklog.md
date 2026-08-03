# Worklog

## 2026-08-03 — Project bootstrap and source framing

### Objective

Convert the initial product discussion into a verifiable project contract and
identify the source categories required before schema design.

### Decisions

- First user: moving-company billing or audit professional.
- First outcome: identify unsupported, missing, underbilled, overbilled, or
  incorrectly paid domestic military-move charges with source-backed explanations.
- Financial relationship: TSP bills the government.
- Program: domestic DP3 governed by 400NG.
- Operation mode: read-only post-audit.
- Final verifier: at least 25 authorized anonymized historical files with
  expert-approved outcomes.
- Interim data: authoritative public sources plus synthetic boundary cases.
- Historical data will be pursued separately and cannot be ingested without
  written authorization and sanitization.

### Evidence gathered

- USTRANSCOM publishes annual business rules, amendments, rate files, advisories,
  transit tools, approved-provider lists, and DTR materials.
- DTR Appendix A-A describes invoice/BL relationships, line identifiers,
  submission methods, acknowledgement/error transactions, evidence retention,
  and line-level approval behavior.
- DD Form 619 exposes shipment, party, accessorial, location, signature, and date
  fields.
- DTEB specifications and reference tables can contribute exact data types,
  lengths, controlled values, and repeating-group constraints.

### METHOD

The interview-before-scaffold sequence exposed a material scope distinction
between government billing and private agent compensation before schema work.

### Next

Red-pen and ratify `goal.md`, then archive and extract the P0 source set.

## 2026-08-03 — Goal ratification

### Decision

The user reviewed the consolidated goal and approved it without changes. The
project contract is ratified. M1 source archival and extraction may begin.

### Next

Archive and checksum the initial 400NG, Tender of Service, TPPS, and DD Form 619
sources, then replace provisional schema discoveries with reviewed findings.

## 2026-08-03 — First source archival and schema extraction

### Archived

- 2026 400NG tariff.
- 2026 Tender of Service Change 1.
- DTR Part IV Appendix A-A (TPPS).
- 2026 400NG baseline rates.
- 2026 transit-time tables.
- DP3 item-code listing dated 2022-08-12.
- DPS mileage/transit-time/SIT workbook.

Checksums and retrieval metadata are in `sources/source-manifest.csv`.

### Reviewed

- Rendered and visually checked 400NG Item 4 pages 19, 21, and 22.
- Rendered and visually checked TPPS pages IV-A-A-12 and IV-A-A-15.
- Rendered and visually checked Tender of Service page 26.

### Schema findings

- Weight observations, tickets, and controlling-weight decisions require separate
  records.
- Performed service, governing tariff item, and billed item code are distinct.
- Invoice-line status must be an event history.
- Invoice submissions and EDI acknowledgements/errors are repeating events.
- Evidence must link to the fact or charge it supports.

### Limitation

The official DD Form 619 server returned HTTP 403 for direct archival. The form
remains provisionally extracted from the official web-rendered source and its
embedded DTR representations. The spreadsheet runtime required by the spreadsheet
skill was not available, so the archived XLSX contents were not opened with an
alternate library.

### Additional DTR coverage

- Archived Chapter A-402, Shipment Management, dated 14 July 2026.
- Archived and visually reviewed relevant portions of Chapter A-413, Government
  Bill of Lading, dated 4 February 2026.
- Added reviewed discoveries for SCAC format, shipment sequencing, date roles,
  authority, extra stops, TCN, consignee/origin roles, paying office, and funding
  references.

## 2026-08-03 — Schema discovery readability

- Replaced the seven-column discovery matrices with compact three-column indexes
  and corresponding schema-mapping lists.
- Preserved all 55 discovery IDs, source locators, candidate mappings, logical
  types, cardinalities, and notes.
- Aligned the remaining Markdown tables for readable plain-text editing.

## 2026-08-03 — Chapter A-402 lifecycle and SIT extraction

### Objective

Extract the shipment-date, arrival, delivery, and storage-in-transit concepts
needed to extend the provisional schema without implementing tariff calculations.

### Reviewed

- DTR Part IV Chapter A-402, publication 14 July 2026, sections C.3, C.7, C.9,
  D.1–5, and F.5–8.
- Rendered PDF pages 7, 9–11, 15–19, and 28–31 were visually checked against the
  derived text; cross-page numbering and continuations were confirmed.

### Schema findings

- Added `DISC-0056` through `DISC-0071` for typed shipment dates, pre-move
  observations, arrival and delivery events, partial deliveries, SIT episodes,
  authorization, control identifiers, dates, extensions, release calculations,
  split portions, conversion, operational gates, and status history.
- Modeled SIT as an episode rather than a shipment flag. Split portions may have
  separate episodes, control identifiers, and weight-ticket evidence.
- Preserved counseling, booking, agreed, calculated, offered, scheduled, and
  actual dates as separate observations.
- Kept DPS operational prerequisites distinct from legal charge eligibility.

### Verification and limitations

- The 16 new discoveries identify the source ID, publication date, retrieval
  date, page/section locator, interpretation status, logical type, cardinality,
  and unresolved tariff questions.
- Initial SIT duration, charge-effective dates, split-shipment minimum weights,
  and contact-attempt evidence still require reconciliation with 400NG and other
  entitlement sources before implementation.

### Next

Inspect the archived rate, item-code, transit-time, and mileage/SIT workbooks,
then continue 400NG service and rate extraction toward the logical schema.
