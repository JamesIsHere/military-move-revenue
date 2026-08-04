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

## 2026-08-03 — First physical source/rule registry increment

### Objective

Create the smallest physical registry that verifies archived-source identity,
claim provenance, and conflict publication gates without prematurely choosing a
database or implementing tariff calculations.

### Change

- Committed the prior source-research and logical-schema work as `d187246`.
- Added a version-controlled JSON registry joined to the existing source
  manifest. It registers all nine archived source versions, nine precise
  locators, nine archived-source claims, three candidate publication
  observations, three open conflicts, and four non-executable draft rule
  candidates.
- Kept the unarchived PPA and legacy-library observations separate from source
  versions and archived source claims.
- Added deterministic validation for repository scope, manifest completeness,
  raw artifact paths, byte lengths, SHA-256 hashes, provenance relationships,
  reciprocal conflict gates, interpretation decisions, and rule-package
  publication constraints.
- Added one valid and five deliberately invalid synthetic registry cases for
  open-conflict publication, missing provenance, candidate-observation
  promotion, unsupported conflict resolution, and missing raw artifacts.

### Verification

`python scripts/validate_source_rule_registry.py` passed the physical registry,
recomputed all nine artifact hashes, accepted the valid draft case, and rejected
all five negative cases for their expected reasons. Existing logical-schema
validation, Python compilation, and repository diff checks are run again at the
handoff.

### Limitation

The JSON representation is the first physical contract, not a final database
choice. It publishes and executes no tariff rule. CF-0001, CF-0002, and CF-0003
remain open and block all affected draft rules.

### Next

Choose the first conflict-free charge or reference family for implementation,
then extend the registry with immutable version/supersession records and
source-backed boundary tests. Continue pursuing archivable PPA artifacts in
parallel.

## 2026-08-03 — Initial scale-weight reference rules

### Objective

Implement the first deterministic 400NG reference family without relying on an
open source conflict, disputed billing item code, or unresolved rate table.

### Selection

Selected initial shipment weight determination and weight-ticket sufficiency
from 400NG Item 4.1, 4.9(a)-(e), and 4.10(a)-(d). Reweigh fees, automatic-reweigh
selection, constructive article weights, refunds, and charge rating remain out
of this increment.

### Change

- Added seven reviewed Item 4 claims and exact locators to the physical registry.
- Added a separate published `2026.weight-determination.1` package with four
  implemented rules for exact net scale weight, scale-method eligibility,
  weighing conditions, and ticket sufficiency.
- Declared eleven input dependencies and two evidence requirements. Candidate
  defaults are prohibited for missing weights, units, scale facts, weighing
  conditions, and ticket content.
- Implemented exact-decimal `gross - tare` evaluation in
  `rules/weight_determination.py`. A final result exposes inputs, calculation
  steps, units, evidence IDs, package/rule IDs, and source provenance.
- Invalid or incomplete evidence produces a `BLOCKED` result with human review
  reasons and no authoritative calculation.
- Added fourteen explicitly synthetic cases covering tare-first and gross-first
  sequences, the 1,000/1,001-pound platform boundary, containerization, combined
  tickets, required ticket content, certification, true copies, vehicle/container
  continuity, positive net weight, exact-decimal strings, and explicit units.

### Verification

- `python scripts/validate_weight_determination.py` passed all 14 cases.
- `python scripts/validate_source_rule_registry.py` accepted the registry and
  rejected six deliberate provenance/publication mutations, including a
  published rule with no declared dependencies.
- Full logical-schema validation, Python compilation, and `git diff --check` are
  run at the handoff.

### Limitation

This package determines an initial reference weight and evidence sufficiency; it
does not calculate an expected invoice amount. It accepts only initial scale
weighings and does not resolve any reweigh, item-code, rate-date, transit, or SIT
question.

### Next

Implement the conflict-free automatic-reweigh requirement decision from Item
4.8 as the next small reference rule, using explicit grade category and initial
weight inputs with threshold boundary tests. Keep reweigh fee billing and
controlling-weight selection separate.

## 2026-08-03 — Item 4.8 automatic-reweigh requirement

### Objective

Implement the automatic-reweigh threshold decision without combining it with
reweigh fee eligibility, billing codes, tolerances, or controlling-weight rules.

### Source check

- Reviewed 400NG Item 4.8(a)-(b), p. 20: E-1 through E-5 uses a 4,000-lb
  inclusive threshold; E-6 through O-10 and DoW civilians use a 7,000-lb
  inclusive threshold; automatic reweighs do not require preapproval.
- Searched the archived 2026 Tender and DTR Chapter A-402 extracts. The Tender
  defers reweighing to 400NG, and the DTR passages address requested reweighs;
  neither supplies a competing automatic threshold.

### Change

- Added locator `LOC-0018` and reviewed claims `CLM-0020`-`CLM-0022`.
- Added a separate published package `2026.automatic-reweigh.1`, rather than
  changing the already-published initial-weight package.
- Declared dependencies on a final initial net scale weight and an explicit
  automatic-reweigh grade band, plus a grade-band evidence requirement.
- Implemented `rules/automatic_reweigh.py`. It returns the required/not-required
  boolean, inclusive threshold, exact initial weight, units, preapproval
  behavior, evidence, and provenance.
- Unmapped grade bands and blocked upstream weights produce `BLOCKED` results
  with no eligibility boolean. The rule does not infer an individual grade.
- Added ten synthetic cases covering 3,999/4,000 and 6,999/7,000 boundaries,
  both stated 7,000-lb categories, an unmapped warrant-grade band, upstream
  weight blocking, result-package tampering, and evidence-status mismatch.

### Verification

`python scripts/validate_automatic_reweigh.py` passed all ten cases. Full source
registry, initial-weight, logical-schema, compilation, and diff validation are
run again at handoff.

### Limitation

Item 4.8 says the earlier tolerances apply, but those tolerances concern the
charge and subsequent reweigh handling, not whether the automatic reweigh must
occur. This increment therefore does not determine a fee, billed item code,
controlling weight, refund, or reimbursement.

### Next

Reconcile the controlling-weight and refund claims across 400NG Items 4.5 and
4.11-4.13 with Tender paragraph 9.a.(2)(c)-(d) before implementing any post-
reweigh weight selection. Preserve competing scope statements if they do not
normalize to one rule.

## 2026-08-03 — Post-reweigh source and scope reconciliation

### Objective

Determine whether 400NG and the Tender conflict on post-reweigh controlling
weight, and isolate any unresolved input before implementing a selector, fee, or
refund rule.

### Reviewed

- Rendered and visually checked 400NG Item 4.5, p. 19; Items 4.11-4.13, pp.
  22-23; and Note 2, p. 23.
- Rendered and visually checked Tender Weighing Shipments 8.a.(2)(c)-(d), printed
  p. 20.
- Checked DTR Chapter A-402 section D.7.b, p. IV-A-402-20, for the operational
  reweigh facts and ticket-submission requirement.

### Reconciliation

- No 400NG-versus-Tender conflict was recorded for the general lower-weight
  obligation. The Tender supplies the general lower-of-two invoicing/refund
  duty; Item 4.5 governs separate fee eligibility; Items 4.11-4.13 add evidence,
  billing holds, and containerized correction paths; Note 2 governs duplicate
  reweighs.
- Recorded ten reviewed claims (`CLM-0023`-`CLM-0032`) and ten precise locators.
- Added `docs/reweigh-controlling-weight-reconciliation.md` with normalized
  questions, source roles, interim behavior, and implementation boundaries.

### New ambiguity

Registered `CF-0004` because Items 4.5 and 4.13 do not state which weight fact
selects the 5,000-lb absolute-versus-percentage tolerance branch. Candidate facts
can fall on opposite sides of the boundary and change fee or reimbursement
eligibility.

Added two non-executable draft rules for the affected tolerance decisions. Both
declare their inputs, evidence, source claims, and reciprocal CF-0004 block. The
general lower-weight observation model remains unblocked.

### Verification

`python scripts/validate_source_rule_registry.py` passed the registry and rejected
seven negative cases, including an attempted CF-0004 publication. Full rule and
schema validators, Python compilation, and diff checks are run at handoff.

### Limitation

No completed-reweigh selector, fee, refund amount, reimbursement amount, billing
code, or invoice adjustment was implemented. Closing CF-0004 requires governing
clarification or an approved scoped interpretation plus 5,000-lb boundary tests.

### Next

Model immutable completed and duplicate reweigh observations with gross, tare,
net, ticket, date, DPS-update, and supersession history. Then implement the
non-tolerance lower-net selection from reviewed claims without crossing CF-0004.

## 2026-08-03 — Registry and weight-reference checkpoint

Checkpointed the physical registry, initial scale-weight package, Item 4.8
automatic-reweigh package, synthetic validators, post-reweigh reconciliation,
and CF-0004 for a clean-context restart. The cold-resume state points next to
immutable completed/duplicate reweigh observations and the non-tolerance
lowest-completed-net selector.

## 2026-08-03 — Immutable reweigh-observation history

### Objective

Model and verify completed, duplicate, and corrected reweigh observations before
implementing any controlling-weight selector, fee, tolerance, or refund rule.

### Source basis

- 400NG Item 4 Note 2, p. 23 (`CLM-0029`), for retaining multiple reweighs as
  separate observations.
- DTR Chapter A-402 section D.7.b, p. IV-A-402-20 (`CLM-0032`), for gross, tare,
  net, ticket, reweigh-date, and DPS-update evidence.
- The ratified project policy for append-only correction and supersession.

### Change

- Tightened the logical weight contract with stable observation keys, contiguous
  versions, completion status, record time, direct supersession, and correction
  reasons.
- Added a DPS reweigh-update event whose required fact roles are gross, tare,
  net, ticket number, and reweigh date.
- Added `SYNTH-LS-005`, containing two distinct completed reweighs and a late
  correction to the second. The correction creates new event, ticket-document,
  measurement, evidence, and DPS-update records while preserving version one.
- Extended the logical fixture validator to enforce exact decimal net arithmetic,
  one current version per observation, reviewed ticket evidence, DPS fact
  coverage, and matching event/ticket/update supersession chains.
- Added a deliberate missing-net mutation and confirmed that it is rejected.

### Verification

`python scripts/validate_logical_schema_fixtures.py` passed all five positive
scenarios and all five negative probes. Source/rule registry, initial-weight, and
automatic-reweigh validators passed. `python -m compileall -q rules scripts` and
`git diff --check` passed; diff check emitted only line-ending conversion
warnings.

### Limitation and next

This increment stores observations only. It does not choose the lowest completed
reweigh, compare that weight with the initial weight, apply CF-0004 tolerances,
or produce a financial result. Next, implement the reviewed non-tolerance
lowest-completed-net selector using only current completed observation versions
with explicit ticket and DPS-update evidence.

## 2026-08-03 — Lowest current completed reweigh selection

### Objective

Publish and implement the conflict-free duplicate-reweigh net selector without
combining it with initial-weight comparison, tolerances, fees, refunds, billing
codes, or monetary rating.

### Source basis

- 400NG Item 4 Note 2, p. 23 (`CLM-0029`), requires the lowest net scale
  reweigh when more than one reweigh exists.
- DTR Chapter A-402 section D.7.b, p. IV-A-402-20 (`CLM-0032`), requires gross,
  tare, net, ticket number, and reweigh date in DPS plus ticket evidence.
- Both claims were previously rendered, visually verified, registered with
  precise locators, and marked reviewed.

### Change

- Added the immutable published package
  `2026.completed-reweigh-selection.1` and implemented rule
  `RULE-LOWEST-CURRENT-COMPLETED-REWEIGH-NET`.
- Declared five input dependencies and two evidence requirements. The package
  has no open-conflict dependency and does not use CF-0004's disputed branch
  fact.
- Implemented exact-decimal selection across current observation versions only.
  Superseded versions remain in the input history but cannot be candidates.
- Required every current observation to be complete and to have exact
  gross-minus-tare net arithmetic, reviewed determining-ticket evidence, and a
  complete DPS update. Missing or ambiguous facts block the entire selection.
- Preserved equal lowest nets by returning all tied observation IDs rather than
  inventing a source-unsupported tie-break.
- Added eleven explicitly synthetic cases covering corrected versions,
  fractional decimals, ties, missing/unreviewed evidence, missing DPS facts,
  incomplete corrections, malformed supersession, binary numeric input, and
  result-package tampering.

### Verification

`python scripts/validate_completed_reweigh_selection.py` passed all eleven
cases. `python scripts/validate_source_rule_registry.py` accepted the new
published package and continued rejecting all seven expected invalid registry
mutations. Focused compilation and `git diff --check` passed; diff check emitted
only line-ending conversion warnings.

### Limitation and next

The result is only the lowest current completed reweigh net. It does not compare
that result with the initial shipment weight or declare a billed/controlling
weight, and it makes no tolerance or financial decision. Next, implement the
separate reviewed lower-of-initial-and-selected-reweigh reference decision while
keeping CF-0004-dependent behavior blocked.

## 2026-08-03 — Initial-versus-reweigh lower-weight reference

### Objective

Publish and implement the general lower-of-two scale-weight reference while
keeping charge-specific billing, constructive/containerized paths, tolerances,
fees, refunds, and money outside the rule.

### Source basis

- Tender of Service Change 1, Weighing Shipments 8.a.(2)(c), printed p. 20
  (`CLM-0030`), supplies the general lower-of-initial-and-reweigh obligation.
- The new rule intentionally does not cite 400NG Item 4.11(d)'s narrower
  within-tolerance statement, so it neither depends on nor bypasses `CF-0004`.
- The upstream initial and completed-reweigh packages provide their own exact
  source and evidence histories.

### Change

- Added the immutable published package
  `2026.scale-reweigh-lower-reference.1` with one implemented exact-decimal
  quantity-selection rule.
- Declared two upstream rule-result dependencies and two corresponding evidence
  requirements. Only provenance-complete results from the published
  initial-weight and completed-reweigh packages are accepted.
- Implemented lower initial, lower completed reweigh, and equal-weight `TIE`
  outcomes. The result exposes both comparison inputs and the selected reweigh
  observation IDs without declaring a charge-specific billed weight.
- Blocked upstream results propagate their own reason lists. Unknown packages,
  altered provenance, invalid units, and result-package tampering are rejected.
- Added eleven explicitly synthetic cases covering lower/higher/tie outcomes,
  fractional pounds, single and dual upstream blockers, unit/provenance/package
  tampering, and downstream result tampering.

### Verification

`python scripts/validate_scale_reweigh_lower_reference.py` passed all eleven
cases. `python scripts/validate_source_rule_registry.py` accepted the fifth
package and thirteenth rule while continuing to reject all seven expected
invalid mutations. Focused compilation and `git diff --check` passed; diff check
emitted only line-ending conversion warnings.

### Limitation and next

This result is a scale-weight reference, not a universal billed weight. It does
not cover the constructive-weight or containerized paths, decide which charges
change, apply tolerances, or calculate a refund or invoice. Next, model the
constructive-weight facts and evidence required by `CLM-0025` before publishing
that separate reference path.

## 2026-08-03 — Constructive-weight fact and evidence contract

### Objective

Model and verify the facts that must exist before calculating a general shipment
constructive weight, without yet publishing the 7-lb-per-cubic-foot rule or
producing a weight result.

### Source basis

- 400NG Item 4.11(e), p. 22 (`CLM-0025`), states the lesser-of-valid-ticket and
  PPSO constructive-weight obligation and the 7-lb-per-cubic-foot factor.
- DTR Chapter A-402 section D.8.c.(1)(a), p. IV-A-402-30, states that scales must
  be unavailable/impractical or tickets lost and that the responsible PPSO must
  approve the constructive-weight method.
- Added reviewed locator `LOC-0029` and direct claim `CLM-0033` for the DTR
  eligibility and approval conditions. The page was within the previously
  rendered and visually reviewed A-402 pp. 28-31 set.

### Change

- Added logical contracts for immutable shipment-volume observations,
  constructive-weight approval events, and readiness assessments.
- Kept verified cubic volume separate from the source-backed 7-lb factor; the
  factor remains a future rule constant rather than a shipment fact.
- Required a supported eligibility reason, responsible-PPSO approval, reviewed
  volume and approval evidence, and resolved ticket status. A valid ticket needs
  a published result reference and reviewed ticket evidence; documented lost
  tickets remain a separate allowed status.
- Added `SYNTH-LS-006` with a positive exact-decimal volume, synthetic evidence
  documents, PPSO approval, and valid-ticket input. The scenario explicitly has
  no calculated article weight, weight determination, or rule decision.
- Added a negative probe that changes PPSO approval to denial and verifies that
  the ready assessment is rejected.

### Verification

`python scripts/validate_logical_schema_fixtures.py` passed all six positive
scenarios and all six negative probes. The physical source/rule registry
validator accepted `LOC-0029` and `CLM-0033` and continued rejecting all seven
expected invalid mutations. Focused compilation and `git diff --check` passed;
diff check emitted only line-ending conversion warnings.

### Limitation and next

No constructive weight has been calculated. Next, publish a separate package
that consumes this verified fact/evidence contract, calculates exact
`volume_cu_ft * 7 lb/cu_ft`, and selects the lower valid-ticket or constructive
reference while preserving documented ticket unavailability.

## 2026-08-03 — Constructive-weight calculation and reference selection

### Objective

Publish the exact general-shipment constructive-weight calculation and select
the lower valid-ticket or constructive reference without introducing rounding,
fees, tolerances, refunds, billing codes, or money.

### Source basis

- 400NG Item 4.11(e), p. 22 (`CLM-0025`), supplies the 7-lb-per-cubic-foot
  factor and lower-of-valid-ticket-and-constructive selection.
- DTR Chapter A-402 section D.8.c.(1)(a), p. IV-A-402-30 (`CLM-0033`), supplies
  the eligibility reasons and responsible-PPSO approval gate.
- Both rules cite both reviewed claims. Neither depends on `CF-0004`.

### Change

- Added published immutable package `2026.constructive-weight-reference.1`
  containing separate calculation and selection rules.
- Declared three calculation dependencies, three selection dependencies, and
  three evidence requirements covering verified volume, PPSO approval, and
  either a valid published ticket result or documented ticket unavailability.
- Implemented exact Decimal multiplication with an explicit
  `NONE_SOURCE_DOES_NOT_SPECIFY_ROUNDING` record. Fractional pounds are retained
  for later rule packages rather than silently rounded.
- Compared a provenance-complete scale-ticket reference with constructive weight
  when available. Equal values produce `TIE`; documented lost tickets select
  constructive weight and omit the unavailable ticket value entirely.
- Missing or unreviewed volume/approval evidence, unsupported eligibility,
  denied approval, and blocked upstream ticket results produce blocked results
  with no calculation or selection.
- Added fifteen synthetic cases covering exact decimals, both lower branches,
  ties, documented lost tickets, evidence and approval blocks, upstream blocks,
  malformed units/numbers/provenance/references, incompatible inputs, and result
  tampering.

### Verification

`python scripts/validate_constructive_weight_reference.py` passed all fifteen
cases. The registry validator accepted the sixth package and two new published
rules while continuing to reject all seven expected invalid mutations. Focused
compilation and `git diff --check` passed; diff check emitted only line-ending
conversion warnings.

### Limitation and next

The output is a weight reference, not a charge-specific billed weight or a
financial result. It does not cover the containerized provisional/correction
path or `CF-0004` tolerances. Next, model the immutable containerized original
tare, new gross, provisional net, and later new-tare observations before
publishing only the conflict-free provisional calculation.

## 2026-08-03 — Containerized provisional and later-completion fact model

### Objective

Model the immutable facts for the containerized gross-only provisional path and
later new-tare completion without calculating a provisional net or crossing the
`CF-0004` reimbursement-tolerance gate.

### Source basis

- 400NG Item 4.13(1)-(2), p. 22 (`CLM-0027`), permits provisional use of new
  gross and origin/original tare and states `new gross - original tare`.
- Item 4.13(3)-(5), pp. 22-23 (`CLM-0028`), requires later new-tare completion
  and describes reimbursement behavior whose 5,000-lb branch input remains
  disputed under `CF-0004`.
- Both passages were previously rendered, visually verified, and registered
  with reviewed claims and precise locators.

### Change

- Added logical contracts for a containerized reweigh case, a linked later
  completion event, and the future provisional result record.
- Added `SYNTH-LS-007` with separate original-tare, new-gross, and new-tare
  weighing events, ticket documents, typed measurements, exact pound units,
  reviewed evidence, and chronological record times.
- Kept the later new tare as a completion event rather than overwriting the
  earlier provisional state.
- Marked the provisional inputs `READY_FOR_DETERMINISTIC_RULE` with no result yet,
  while scoping `CF-0004` only to reimbursement tolerance.
- Added validation for positive provisional inputs, shipment consistency,
  original/provisional/completion chronology, exact ticket/evidence linkage,
  absence of premature net calculations, and the conflict hold.
- Added a negative probe that attempts to mark reimbursement tolerance evaluated
  and confirmed that validation rejects it.

### Verification

`python scripts/validate_logical_schema_fixtures.py` passed all seven positive
scenarios and seven negative probes. Focused compilation and `git diff --check`
passed; diff check emitted only line-ending conversion warnings.

### Limitation and next

No provisional net or lower reference has been calculated. Next, publish a
separate `CLM-0027` package for exact `new gross - original tare` and lower-of-
initial/provisional selection, while treating the later new tare as evidence and
leaving every `CLM-0028` tolerance decision blocked by `CF-0004`.

## 2026-08-03 — Containerized provisional-weight package

### Objective

Publish the conflict-free `CLM-0027` calculation and lower-selection rules
without evaluating the later `CLM-0028` reimbursement tolerance.

### Source basis

- 400NG Item 4.13(1)-(2), p. 22 (`CLM-0027`, `LOC-0023`), directly states use
  of new gross and original tare, the provisional subtraction, and use of the
  lesser weight.
- Item 4.13(3)-(5) (`CLM-0028`) and `CF-0004` are explicitly excluded because
  they govern the later new-tare reimbursement path and disputed tolerance
  branch input.

### Change

- Published immutable package `2026.containerized-provisional-weight.1` with
  separate exact-calculation and lower-selection rules, both sourced only to
  reviewed `CLM-0027`.
- Declared original-tare, new-gross, final-initial-result, and provisional-result
  dependencies plus reviewed ticket and upstream-result evidence requirements.
- Implemented exact Decimal subtraction with no source-invented rounding and
  lower initial/provisional selection with explicit tie handling.
- Validated the exact upstream initial-weight package, rule set, provenance,
  status, and units before selection.
- Blocked missing or unreviewed ticket evidence, non-ready cases, nonpositive
  provisional inputs, and blocked upstream results without emitting a weight.
- Added fifteen synthetic cases covering exact fractional subtraction, both
  lower branches, ties, later-new-tare isolation, evidence/readiness/upstream
  blocks, unit and chronology errors, provenance, and result tampering.

### Verification

`python scripts/validate_containerized_provisional_weight.py` passed all fifteen
cases. The physical registry validator accepted seven packages and seventeen
rules while continuing to reject all seven expected invalid mutations. Focused
compilation and `git diff --check` passed; diff check emitted only line-ending
conversion warnings.

### Limitation and next

The output is a provisional weight reference, not a completed reweigh,
charge-specific billed weight, reimbursement decision, or monetary result. The
later new-tare facts cannot affect it. Next, model immutable reweigh refund,
billing-hold, and supplemental-adjustment workflow facts from `CLM-0026`,
`CLM-0031`, and `CLM-0032` before implementing any financial calculation.

## 2026-08-03 — Reweigh refund and billing-hold workflow fact model

### Objective

Model the post-invoice lower-reweigh workflow as immutable facts and evidence
without calculating a refund, fee, tolerance, expected charge, or payment.

### Source basis

- 400NG Item 4.12(a)-(c), p. 22 (`CLM-0026`, `LOC-0022`), requires the refund
  workflow and restricts destination/direct-delivery invoicing until the reweigh,
  DPS update, tickets, and applicable refund processing are complete.
- Tender Weighing Shipments 8.a.(2)(d), printed p. 20 (`CLM-0031`, `LOC-0027`),
  requires a supplemental invoice to refund reduced charges when reweigh occurs
  after initial invoicing.
- DTR Chapter A-402 section D.7.b, p. IV-A-402-20 (`CLM-0032`, `LOC-0028`),
  requires gross/tare/net, ticket number, and date in DPS plus weight-ticket
  delivery to the ordering PPSO within seven working days.

### Change

- Added logical contracts for a reweigh-refund case, PPSO ticket-delivery event,
  append-only refund-adjustment events, and append-only billing-hold events.
- Added `SYNTH-LS-008` with an approved original invoice that remains unchanged,
  a distinct negative-supplemental invoice identity with no monetary version,
  an exact completed reweigh, reviewed determining ticket, complete DPS update,
  and reviewed PPSO delivery evidence.
- Preserved refund-required, supplemental-submitted, and processed-for-payment
  states as a chronological predecessor chain rather than a mutable status.
- Preserved hold placement and release separately and required release to follow
  the DPS update, ticket delivery, and refund-processed event.
- Prohibited refund amounts, signed adjustments, tolerance results, reweigh fees,
  calculations, expected charges, reconciliation matches, payments, and rule
  decisions in this fact-only scenario.
- Added a negative probe that moves hold release before refund processing and
  confirms validation rejects the history.

### Verification

`python scripts/validate_logical_schema_fixtures.py` passed all eight positive
scenarios and eight negative probes. Focused compilation and `git diff --check`
passed; diff check emitted only line-ending conversion warnings.

### Limitation and next

The model records workflow facts but does not decide whether a supplemental
refund is required or whether a hold may release. Next, publish a conflict-free,
non-monetary workflow package for those decisions using `CLM-0026`, `CLM-0031`,
and `CLM-0032`; keep all refund amounts and `CF-0004` tolerance logic out.

## 2026-08-03 — Post-invoice reweigh refund workflow package

### Objective

Publish deterministic, non-monetary decisions for supplemental-refund necessity
and destination/direct-delivery hold-release readiness.

### Source basis

- 400NG Item 4.12(a)-(c), p. 22 (`CLM-0026`, `LOC-0022`), supplies refund scope
  and hold prerequisites.
- Tender Weighing Shipments 8.a.(2)(d), printed p. 20 (`CLM-0031`, `LOC-0027`),
  supplies the post-invoice supplemental-refund requirement.
- DTR A-402 D.7.b, p. IV-A-402-20 (`CLM-0032`, `LOC-0028`), supplies required
  DPS facts and PPSO ticket-delivery evidence.

### Change

- Published immutable package `2026.reweigh-refund-workflow.1` with separate
  supplemental-refund and hold-readiness rules and no conflict dependency.
- Declared verified lower-weight result, original invoice submission, completed
  reweigh, DPS update, PPSO ticket delivery, and conditional refund-processing
  dependencies and evidence requirements.
- Added an immutable original invoice submission event to `SYNTH-LS-008` so the
  post-invoice branch uses an explicit submission time rather than a proxy.
- Implemented exact upstream package/rule/provenance validation and required the
  selected reweigh observation to match the workflow case.
- Made refund processing conditional: it blocks hold release only when a lower
  reweigh occurred after initial invoice submission.
- Returned known incomplete workflow states as final `release_ready: false`,
  while missing/unreviewed facts or evidence produce blocked human-review output.
- Added sixteen cases covering both refund branches, ready/not-ready holds,
  conditional processing, DPS/ticket/refund evidence, incomplete fact coverage,
  chronology, upstream blocks, provenance, references, and result tampering.

### Verification

`python scripts/validate_reweigh_refund_workflow.py` passed all sixteen cases.
The registry validator accepted eight packages and nineteen rules while still
rejecting all seven expected invalid mutations. Logical-schema validation passed
all eight scenarios and negative probes; focused compilation and diff checks
passed with only line-ending warnings.

### Limitation and next

The package emits workflow booleans and reasons only. It does not calculate a
refund, expected charge, fee, tolerance, billing item, or payment. Next, inspect
the archived tariff/rate/item-code evidence and select the first monetary charge
family whose full provenance is complete enough for deterministic shadow rating.

## 2026-08-03 — Reweigh implementation checkpoint

### Outcome

Prepared one cold-resume commit containing the immutable reweigh-observation
model, completed/lower/constructive/containerized weight packages, post-invoice
refund workflow model and package, synthetic fixtures, validators, registry
updates, and documentation accumulated after `de53303`.

### Verification

The checkpoint passes all logical-schema, physical-registry, initial-weight,
automatic-reweigh, completed-reweigh, scale-lower-reference, constructive-weight,
containerized-provisional, and reweigh-refund-workflow suites. Python compilation
and `git diff --check` pass; diff check reports only line-ending conversion
warnings.

### Resume point

Inspect the archived 400NG, baseline-rate workbook, and item-code evidence to
select the first conflict-free monetary charge family for shadow rating. Record
an exact source gap instead of implementing if effective date, rate cell, unit,
rounding, item-code currency, or evidence provenance is incomplete.

## 2026-08-03 — First monetary charge-family inventory

### Objective

Select the narrowest source-complete monetary family for initial shadow rating,
or record the exact publication gate if no family is complete.

### Source basis

- Reviewed 2026 400NG Items 1.2(c), 4, 28, 50, 105, 120, and 130 against the
  archived PDF/text extraction.
- Re-read the 2026 Baseline Rates `Additional Rates` candidate cells and the
  archived 12 August 2022 `DOM_400NG` billing rows and legends.
- Applied open conflicts `CF-0001` through `CF-0004`, especially the current
  item-code publication gap in `CF-0003`.

### Change

- Added `docs/monetary-charge-family-inventory.md` with a provenance matrix for
  Item 28A, reweigh, bulky article, extra labor, crating, and full pack/unpack.
- Selected Item 28A extra pickup as the preferred first family because its
  candidate math is a flat 198.50 USD per eligible performed occurrence and its
  tariff evidence boundary is narrower than the alternatives.
- Did not implement or register a monetary rule. The only complete source for
  Item 28A's requested-pickup date basis, `EA` unit, `SC` reference, additional-
  pickup location, approval screen, and approval flag is the disputed 2022 item
  listing. `CF-0003` must close first.

### Verification

The archived rate workbook was inspected read-only and confirmed
`Additional Rates!A13:F13`; the item-code workbook confirmed row 23 and legends
155-159; the extracted tariff confirmed the Item 28 eligibility text and Items
1.2(c)/50 effective-date interaction. Existing rule code and registry data were
not changed.

### Limitation and next

No fee, expected charge, billing line, reconciliation, or payment result is
implemented. Next, obtain an authoritative current item-code baseline or a
scoped approval that closes the Item 28A portion of `CF-0003`, then publish the
package with Decimal and evidence-boundary tests.

## 2026-08-03 — Item 28A scoped source interpretation

### Objective

Archive the current official publication state and approve only the Item 28A
source contract needed for the first shadow-rating package without generalizing
the 2022 Item Code Listing.

### Source basis

- Downloaded the unauthenticated USTRANSCOM DP3 public-library page from its
  canonical URL and preserved the 374,079-byte raw HTML with SHA-256
  `0474F523B827DBEE09CC676AF3177AB6DC33E6F4DAB9640ADFEAE95BCC2150E5`.
- Verified HTML line 4697 links the exact archived
  `Item Code Listing (12 Aug 2022).zip` artifact.
- Reconciled that publication evidence with 2026 400NG Items 1.2(c) and 28,
  `Additional Rates!A1` and `A13:F13`, and `DOM_400NG!A23:Q23` plus legends.
- Retained the unarchived PPA publication-location observation as candidate and
  did not treat search-result absence as supersession proof.

### Change

- Added the public-library HTML to the source manifest and physical registry,
  with an exact locator and reviewed publication-state claim.
- Added reviewed Item 28A eligibility, 198.50 USD-per-occurrence rate, and
  billing-contract claims.
- Recorded the project owner's explicit approval as Decision 0003 / `INT-0001`.
  It authorizes requested-pickup date basis, `28A`, `EA`, `SC`, `AB`, Origin
  PPSO, and approval-required fields only for the 2026 Item 28A package.
- Kept `CF-0003` open for the complete listing and every other billing item.
- Added a draft scoped source-contract rule linked reciprocally to `INT-0001`.
- Strengthened registry validation and added two negative cases for missing
  decision-rule reciprocity and missing regression requirements.

### Verification

The physical registry validator passes the checked-in registry and all nine
expected-invalid mutations. JSON parsing, source hash/byte validation, and the
direct HTML link check pass. No raw artifact was modified after retrieval.

### Limitation and next

No money or Item 28A eligibility result is implemented. Next, model immutable
authorization and performed-occurrence facts, then publish the Item 28A
eligibility/count/rating package with exact Decimal and interpretation-boundary
tests.

## 2026-08-03 — Item 28A deterministic shadow rating

### Objective

Publish the smallest source-complete monetary package under Decision 0003 /
`INT-0001`, with exact arithmetic, occurrence-level evidence, effective-date
selection, and mandatory boundary/tamper regression coverage.

### Source and fact boundary

- Reused reviewed claims `CLM-0001`, `CLM-0010`, and `CLM-0034` through
  `CLM-0037`, with their exact source-version and locator relationships.
- Added a Git attribute for `sources/raw/**` so archived evidence is neither
  line-ending-normalized nor treated as an authored text diff.
- Added synthetic logical scenario `SYNTH-LS-009` for immutable requested date,
  ordered stops, performed service, Origin-PPSO decision, documents, document
  versions, and reviewed evidence links. It deliberately contains no money.
- Extended the logical validator with a paired negative probe that rejects an
  Item 28A performance attached to the original pickup instead of an additional
  pickup stop.

### Change

- Published immutable package `2026.item-28a-extra-pickup.1` and its scoped
  source-contract, eligible-occurrence, and expected-charge rules.
- Implemented `rules/item_28a_extra_pickup.py`. It selects the package by
  original requested pickup date, rejects broadened interpretation scope,
  counts only reviewed completed extra pickups after the first, applies the
  self-storage-only exclusion, and requires one reviewed Origin-PPSO decision
  no later than performance.
- Used exact `Decimal("198.50")` multiplication. Blocked facts or evidence emit
  no amount, occurrence count, or expected-line action.
- Added the package's source, dependency, evidence, and reciprocal `INT-0001`
  contracts to the physical registry.
- Added a synthetic case suite and result-contract validator. The validator also
  rejects non-string quantities and altered package, decision, rule sequence,
  provenance, or amount output.

### Verification

- `python scripts/validate_item_28a_extra_pickup.py`: 24 positive, blocked,
  exclusion, and malformed-input cases plus five result-tamper probes pass.
- `python scripts/validate_logical_schema_fixtures.py`: nine positive scenarios
  and nine negative probes pass.
- `python scripts/validate_source_rule_registry.py`: the physical registry and
  all nine expected-invalid mutations pass.
- The case suite proves both rate-cycle edges, before/after blocking, zero/one/
  two occurrences, exact `198.50 * 2 = 397.00`, evidence gates, denial evidence,
  exclusions, duplicates, chronology, units, and decision scope.
- Python compilation and `git diff --check` pass; diff check reports only
  existing line-ending conversion warnings.

### Limitation and next

The package reconstructs only an expected Item 28A shadow charge. It does not
compare invoice or payment records. Next, model immutable synthetic Item 28A
invoice/payment line versions and implement an exact expected-versus-invoiced-
versus-paid comparison before attempting another source-blocked monetary family.

## 2026-08-03 — Item 28A expected/invoiced/paid audit slice

### Objective

Implement the first end-to-end read-only post-audit comparison without changing
the published Item 28A rating package or treating absent invoice/payment data as
zero without a reviewed completeness assertion.

### Source and policy basis

- Re-read the ratified `goal.md`, active M4/M5 plan, logical invoice/payment
  contract, and published Item 28A evaluator boundary.
- Reviewed DTR Appendix A-A paragraphs 3.(17)-(22), printed pp. IV-A-A-7–8,
  and 4.a.(1)-(2)/(9), printed pp. IV-A-A-8 and IV-A-A-12, against the archived
  text. Registered `CLM-0038` through `CLM-0040` for per-line payment data,
  post-payment audit inputs/supporting documents, and line-item identity matching.
- Added versioned internal policy
  `AUDIT-DP3-ITEM-28A-RECONCILIATION-V1` / `2026-08-03.1`. It identifies the
  ratified goal and logical schema as internal provenance and does not present
  comparison formulas as Government tariff rules.

### Change

- Added synthetic logical scenario `SYNTH-LS-010` with a corrected invoice,
  corrected current line, reviewed invoice/remittance documents, exact payment
  allocation, and separate reviewed invoice/payment completeness assertions.
- Extended logical validation for direct supersession, current-version alignment,
  version totals, evidence targets, current payment-allocation balancing, and
  completeness coverage.
- Implemented `rules/item_28a_post_audit.py`. It validates the complete upstream
  Item 28A result contract, selects current immutable invoice/line/allocation
  versions, matches only raw `28A`/`EA` under `INT-0001`, and preserves every
  selected version and evidence ID in the input snapshot.
- Added exact Decimal comparisons:
  `invoiced - expected`, `paid - invoiced`, `paid - expected`, and invoiced
  quantity minus expected occurrence count.
- Added decided billing, quantity, and payment findings for correct, missing,
  unsupported, underbilled, overbilled, unpaid, partially paid, and overpaid
  outcomes. Ambiguity, incomplete history, evidence gaps, or blocked upstream
  rating produces `AUDIT_BLOCKED`, human review, and no comparison amounts.
- Added corrected payment-allocation history so only the current allocation
  version contributes to payment.

### Verification

- `python scripts/validate_item_28a_post_audit.py`: 27 final, blocked, and
  malformed-input cases plus seven result-tamper probes pass.
- `python scripts/validate_logical_schema_fixtures.py`: ten positive scenarios
  and ten negative probes pass.
- `python scripts/validate_source_rule_registry.py`: the physical registry and
  all nine expected-invalid mutations pass with 37 reviewed claims and 34
  locators.
- All prior rule suites pass unchanged; Python compilation and `git diff
  --check` pass, with only line-ending conversion warnings.

### Limitation and next

This is a single-charge synthetic vertical slice, not a batch audit product and
not historical acceptance. No real shipment, invoice, payment, authenticated
system, live submission, or money movement was used. Next, add a deterministic
human-readable audit explanation/report envelope and a reusable charge-adapter
contract before expanding to another source-complete monetary family.

## 2026-08-03 — Deterministic audit report and charge-adapter boundary

### Objective

Render the Item 28A audit as a versioned, canonical report with deterministic
explanations, exact aggregates, sources, evidence, findings, and blockers while
creating a reusable boundary for future source-complete charge families.

### Source and policy basis

- Re-read the ratified goal, M5 plan, Item 28A rating/audit contracts, and
  synthetic invoice/payment fixtures.
- Added internal presentation policy `AUDIT-REPORT-ENVELOPE-V1` version
  `2026-08-03.1`. Its provenance identifies the ratified goal and the policy
  document with version, effective period, locator, retrieval date, and
  interpretation status.
- Published Item 28A audit policy version `2026-08-03.2` because preserving the
  validated upstream calculation/evidence trace changes the result contract;
  the prior `.1` behavior remains reproducible in Git history.

### Change

- Added `CHARGE-ADAPTER-DP3-ITEM-28A-V1`. The registered adapter executes the
  deterministic reconciler and validates its audit policy, audited charge,
  upstream math, provenance, evidence, exact comparison arithmetic, match, and
  finding classification before report inclusion.
- Added schema `audit-report-envelope.v1` with one-shipment/cutoff and one-
  instance-per-charge-family gates, stable charge/finding ordering, exact
  Decimal aggregation, and canonical JSON serialization.
- Added deterministic billing, quantity, payment, and blocker explanations.
  Sources retain report-policy, expected-charge, audit-policy, and observed-
  invoice/payment scopes; evidence retains expected, invoice, payment, and
  completeness IDs.
- Aggregate values are all-or-nothing: any blocked charge emits no report-level
  money. Decided open exceptions retain their authoritative comparison and
  require human review.
- Bound report and adapter `data_status` so a synthetic result cannot be
  relabeled as authorized-sanitized data. No AI-authored financial conclusion
  enters the envelope.

### Verification

- `python scripts/validate_audit_report.py`: four final/blocked end-to-end report
  cases, ten output-tamper probes, and three request-contract probes pass.
- The suite proves stable billing→quantity→payment ordering, one finding per
  blocker, expected math preservation, source/evidence projection, canonical
  round-trip JSON, all-or-nothing totals, data-status binding, unknown-adapter
  rejection, cutoff matching, and duplicate-family rejection.
- `python scripts/validate_item_28a_post_audit.py`: all 27 audit cases and seven
  result-tamper probes pass under policy version `2026-08-03.2`.
- All prior registry, schema, weight, workflow, and Item 28A rating suites pass.
  Python compilation and `git diff --check` pass.

### Limitation and next

The report currently contains one synthetic Item 28A charge family; it is not a
multi-family shipment audit or historical acceptance. No real data, live
submission, or money movement was used. Next, rank candidate monetary families
against a strict source-readiness gate and implement a second adapter only when
its rule, rate, effective-date selector, evidence, and mapping authority are
complete.

## 2026-08-04 — Monetary source-readiness matrix

### Objective and basis

Apply a strict, provenance-backed gate to the next monetary families without
using a score to hide a missing governing dependency. Re-read the ratified goal,
active M1/M3/M4/M5 plan, physical registry, conflict register, source-currency
research, first-family inventory, archived Item 28 text, rate extracts, and
Item-Code rows 23–26.

### Change

- Added internal gate `MONETARY-SOURCE-READINESS-GATE-V1` version
  `2026-08-04.1`. `READY` requires all six dimensions: rule, rate/unit,
  effective-date selector, billing-item contract, evidence contract, and audit
  matching support.
- Added a machine-readable matrix with 16 complete provenance records, five
  closure blockers, the implemented Item 28A reference, and six ranked blocked
  candidates: Item 28B, reweigh fee, Item 130, Item 120, Item 105B, and Item
  105A. SIT, linehaul/shorthaul, and Item 28C remain explicitly unranked.
- Determined that no second family is ready. Item 28B ranks first because its
  current tariff rule and 198.50 USD-per-occurrence rate are direct and its fact
  model can reuse Item 28A, but `CF-0001` and `CF-0003` still block actual-
  pickup rate selection, row-24 continuity, and Destination-PPSO evidence.
- Recommended a narrow Decision 0004 dossier. This assessment does not approve
  that interpretation and produces no rule, adapter, or money.

### Verification and next

- `python scripts/validate_source_readiness_matrix.py`: seven candidates, 16
  provenance records, five blockers, and six tamper probes pass.
- The validator joins every source/version to the manifest and registry,
  requires open conflicts and exact closure targets, enforces all-gates-pass
  readiness, contiguous ranking, and a rank-one blocked recommendation.
- Next, draft the Item 28B decision dossier for owner review; do not implement
  until explicitly approved. If declined, pursue the current domestic item-code
  baseline/advisory chain as the highest-leverage external acquisition.
