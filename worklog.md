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

## 2026-08-03 — 400NG SIT eligibility and rating reconciliation

### Objective

Resume M1 at the workbook-inspection handoff and, when the required spreadsheet
runtime proved unavailable, complete the next source-backed SIT reconciliation.

### Reviewed

- 400NG Item 17 and Items 17-1/17-2, pages 27–32.
- 400NG Item 185, page 57, and Item 210, pages 58–59.
- 400NG Appendix A SIT examples, pages 83–84.
- Rendered pages were visually checked against the archived PDF and derived text.

### Schema findings

- Added `DISC-0072` through `DISC-0081` for SIT rating geography, authorization,
  accrual, split/partial weight bases, custody evidence, attempted-delivery
  evidence, storage and delivery calculations, effective dates, and conversion.
- Resolved that the accepted BL address, not the warehouse, controls SIT rating
  geography; physical storage and rating context require separate records.
- Resolved that overflow storage uses a combined 1,000-lb minimum while partial
  delivery out uses actual weight, including temporary Item 226A billing below
  1,000 lbs.
- Preserved the Appendix A `185E` label versus Item 185/adjacent `185B` text as a
  source conflict requiring interpretation approval.

### Verification and limitation

- Recomputed the archived PDF SHA-256 against the source manifest.
- Checked discovery identifiers for uniqueness and sequence.
- Workbook inspection remains queued because the spreadsheet skill's required
  dependency loader and artifact runtime were unavailable; no alternate parser
  was used.

### Next

Restore the approved spreadsheet runtime, inspect the four archived workbook
families, and map their concrete dimensions to `DISC-0078` through `DISC-0080`.

## 2026-08-03 — Spreadsheet runtime recheck

### Objective

Resume the queued P0 workbook inspection using the approved spreadsheet
workflow.

### Verification

- Re-read the active goal, state, M1 plan, spreadsheet skill, API quick start,
  and formatting requirements.
- Confirmed that no `load_workspace_dependencies` capability is exposed in the
  session.
- Attempted the documented bare import of `@oai/artifact-tool` in the available
  Node-backed runtime; it returned `Module not found`.

### Blocker

The spreadsheet workflow prohibits searching for package paths, installing the
runtime, or substituting an alternate parser without explicit user direction.
Workbook artifacts and repository source files remain unchanged. Progress needs
either a session with the approved loader/runtime or authorization for a
read-only fallback inspection.

## 2026-08-03 — P0 workbook structural inspection

### Objective

Inspect the archived baseline-rate, item-code, transit-time, and mileage/SIT
workbooks and reconcile their dimensions with the 400NG SIT findings.

### Method

- The user explicitly authorized openpyxl after the artifact-tool runtime remained
  unavailable.
- Added `scripts/inspect_archived_workbooks.py` and generated the reproducible
  `sources/derived/2026/workbook-structure.json` extract.
- Read ZIP members in memory; captured formulas and cached values separately;
  performed no workbook recalculation or save.
- Rechecked all four raw artifact hashes against the source manifest.

### Reviewed findings

- Baseline rates: ZIP3/BPC/service-area mappings, service and SIT schedules,
  185A/185B rates, linehaul/accessorial weight bands, and 210A/210D matrices plus
  210B/210E schedule rates.
- Item codes: domestic date-basis, code, fuel, discount, location, unit, EDI,
  note, and approval columns; detailed SIT rows 185A/B, 210A–F, and 226A.
- Transit: the complete 2026 domestic distance-by-weight transit-day matrix and
  Alaska adjustments.
- Mileage/SIT tool: ZIP3-to-table mappings, compressed mileage matrices,
  250-mile transit bracket selection, weight-band selection, and the 70-percent
  authorized-SIT-day expression.
- Added `DISC-0082` through `DISC-0091` and expanded the conceptual model.

### Conflicts and limitations

- The baseline workbook's original-requested-pickup-date banner conflicts with
  400NG Item 1.2(c)'s actual-pickup-date exception for SIT/accessorial tables.
- At a synthetic 873 miles and 6,000 lbs, the mileage tool's hidden table returns
  9 transit days while the 2026 domestic table returns 18. The tool has no stated
  effective date.
- The 12 August 2022 item-code listing has no resolved supersession period.
- No workbook rendering engine was available; review was structural and
  cell/formula-level rather than visual.

### Verification

- All 91 discovery identifiers are unique and sequential.
- Source hashes match the manifest; raw workbooks are unchanged.
- Formula and cached-value scans found no cached formula errors in the rate,
  transit, or item-code workbooks. The mileage tool contains five expected cached
  errors in nonselected lookup branches or its blank-weight sample path.

### Next

Document source precedence/conflict handling, locate current item-code and
mileage-tool version authority, and begin the logical schema from the reviewed
workbook dimensions.

## 2026-08-03 — Source precedence and conflict policy

### Objective

Complete the M1 requirement for source precedence and conflict handling, then
apply it to the open workbook interpretation cases.

### Decision

- Accepted Decision 0002: precedence is determined by applicability and the
  question being answered, not by one flat source ranking.
- Governing tariff text controls charge eligibility and date selection;
  incorporated rate packages supply numeric cells; DTR/Tender sources govern
  operational authorization facts; code/EDI sources govern representation and
  cannot independently create financial entitlement.
- Material unresolved conflicts stop only the dependent deterministic decision
  and require a versioned human interpretation; claims remain append-only.

### Applied cases

- Registered `CF-0001` for the tariff versus baseline-workbook SIT/accessorial
  date-selection conflict. Item 1.2(c) is the provisional lead, but no production
  selector is approved.
- Registered `CF-0002` for the explicit 2026 transit table versus the undated
  mileage tool and its 70-percent authorized-SIT-day expression. The 2026 table
  may inform provisional transit schema; SIT entitlement remains unapproved.
- Registered `CF-0003` for the unresolved currency of the 12 August 2022 item-code
  listing. Its values remain provisional.

### Schema impact

- Added source claim, conflict case, conflict-claim, interpretation decision, and
  decision-impact concepts to the provisional conceptual model.
- Defined candidate, reviewed, disputed, approved, and superseded interpretation
  statuses; only approved material interpretations may enter a published rule
  package.

### Verification

- All three cases identify source IDs, versions/effective periods, exact
  locators, retrieval context, interim behavior, required closure evidence, and
  affected discoveries.
- The policy covers financial rules, numeric rates, operational facts, billing
  representation, evidence, and adjudicative interpretation.
- Repository diff validation passed.

### Next

Locate authoritative version/effective metadata for the item-code listing and
mileage/SIT tool, then draft the logical schema from reviewed discoveries.

## 2026-08-03 — Logical schema draft

### Objective

Turn the complete discovery inventory and provisional conceptual model into an
implementation-neutral logical data contract without prematurely selecting a
database engine or approving disputed spreadsheet behavior.

### Change

- Added `docs/logical-schema.md` with the logical type system, cardinality and
  nullability conventions, sensitivity classes, provenance/version metadata,
  and append-only correction rules.
- Defined the logical ER relationships and field contracts for source claims,
  conflicts, rules/rates, controlled vocabularies, parties, shipments, portions,
  dates/events, weight, evidence, service performance, SIT, invoices, submission
  status, payments, rating, reconciliation, findings, and human review.
- Kept external item codes separate from internal service semantics; separated
  actual SIT custody location from rating geography; and kept performance,
  authorization, billing, payment, and audit outcomes as distinct histories.
- Added deterministic calculation records exposing the rule package, exact
  decimal inputs, units, calculation steps, rounding rule, evidence, and
  unresolved assumptions.
- Added explicit production gates for CF-0001, CF-0002, and CF-0003. The disputed
  claims remain recordable but cannot silently select a final financial result.
- Recorded the still-deferred physical choices, including key format, database
  engine, decimal precision, indexes, encryption implementation, and EDI storage.

### Verification

- Checked the schema's required sections, Markdown table shapes, and Mermaid
  fence balance; the structural check passed for the 433-line document.
- Confirmed the discovery inventory is contiguous from `DISC-0001` through
  `DISC-0091` and that the schema coverage matrix spans all 91 discoveries.
- Confirmed each of the three registered conflict cases has an explicit schema
  gate and allowed interim behavior.
- Corrected an initial coverage omission for `DISC-0001`–`DISC-0009` by adding
  entitlement context and mapping the early DD Form 619 identifiers, endpoints,
  pickup date, party roles, and attestations.

### Next

Exercise the logical model with synthetic straight-through and boundary
scenarios, then use the results to tighten conditional cardinalities and prepare
the physical source/rule registry without crossing unresolved conflict gates.

## 2026-08-03 — Synthetic logical-schema validation

### Objective

Exercise the draft logical contract with straight-through and boundary scenarios
before choosing physical database types.

### Change

- Added four explicitly synthetic fixtures covering straight-through billing,
  split SIT, immutable correction history, and a CF-0001/CF-0003-gated audit.
- Added a standard-library validator for record provenance, internal references,
  exact-decimal strings, currency and unit pairing, invoice/payment balance,
  calculation steps, portion-weight reconciliation, SIT release boundaries,
  supersession chains, late-recorded events, and conflict holds.
- Added one deliberately invalid mutation per scenario so each boundary is also
  verified to fail.
- Tightened the logical contract so blocked decisions omit outcomes, unknown
  eligibility omits booleans, unrated findings omit unavailable expected/variance
  amounts, and declared portion weights carry explicit units.

### Verification

`python scripts/validate_logical_schema_fixtures.py` passed all four positive
scenarios and all four negative probes. `python -m py_compile` and
`git diff --check` also passed; the latter reported only existing line-ending
conversion warnings.

### Next

Return to M1 source closure by locating authoritative version/effective metadata
for the item-code listing and mileage/SIT tool, preserving unresolved claims if
the public record does not establish currency.

## 2026-08-03 — Item-code and mileage/SIT source-currency research

### Objective

Locate authoritative version, effective-period, and supersession evidence for
the 2022 Item Code Listing and DPS Mileage Transit Time SIT Tool.

### Findings

- Extracted reproducible XLSX core properties showing the archived mileage/SIT
  tool was last modified on 26 September 2025, before the 2026 transit table was
  published. This is a file-version marker, not an effective date.
- Confirmed the current PPA resource center still publishes a same-titled
  mileage/SIT tool as a quick link, but displays no version/effective date.
- Confirmed the July 2026 DTR says the direct-delivery SIT threshold is a
  solicitation percentage without stating the percentage or rounding rule; no
  governing 70-percent provision was located in the reviewed 2026 domestic
  tariff or Tender text.
- Confirmed the 2026 400NG refers to the legacy USTRANSCOM Item Code Listing and
  that the legacy page still exposes the 12 August 2022 workbook.
- Located PPA Advisory 26-0105, which identifies PPA.mil as the authoritative
  current resource surface. The PPA catalog did not expose the 2022 Item Code
  Listing, creating a publication-location conflict rather than resolving
  continued applicability.
- Recorded PPA Advisory 26-0110 only as out-of-scope corroboration that current
  item-code behavior may be supplemented by advisories; its international rule
  was not imported into domestic v1.

### Change

- Added `docs/source-currency-research.md` and new source-register entries for
  the PPA resource center and Advisory 26-0105.
- Added claims `CLM-0007`–`CLM-0012`; narrowed `CF-0002` and upgraded `CF-0003`
  to a disputed publication-location gap.
- Extended the workbook inspector and derived JSON to preserve raw XLSX core
  property text, including UTC timestamp suffixes.

### Verification and limitation

The workbook structural extract regenerated with all archived artifact hashes
unchanged. Synthetic logical-schema validation and `git diff --check` passed.
Direct PPA.mil/media.defense.gov downloads returned HTTP 403, and no in-app
browser was available, so the PPA page, linked workbook, and Advisory 26-0105
could not be added to the raw archive. Their claims remain candidate rather than
reviewed.

### Next

Obtain the PPA-hosted workbook and Advisory 26-0105 through an accessible public
download path or user-supplied copies, then compare hashes. In parallel, continue
with a conflict-aware source/rule registry that cannot publish the blocked
70-percent or item-code decisions.
