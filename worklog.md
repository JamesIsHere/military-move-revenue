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

## 2026-08-04 — Proposed Item 28B Decision 0004 dossier

### Outcome

- Verified archived 400NG Item 28, `Additional Rates!A13:F13`, Item-Code
  `DOM_400NG!A24:Q24`, and the official-library snapshot.
- Drafted Decision 0004 with status `PROPOSED_OWNER_APPROVAL_REQUIRED`. The
  recommended narrow contract uses actual pickup date, `28B`, `EA`, `SC`, extra-
  delivery location `AE`, Destination PPSO approval, and exact
  `eligible occurrences * 198.50 USD` math through 2027-05-14.
- Preserved both alternatives: `A_APPROVE_NARROW` and `B_DEFER`. `CF-0001` and
  `CF-0003` remain open broadly; Item 28C, related transportation/additional
  services, SIT, broad code validation, live submission, and money movement are
  excluded.
- Added ten mandatory boundary/evidence/Decimal/tamper tests and a hard gate
  prohibiting interpretation registration or financial implementation before
  explicit owner approval.

### Verification and stop

- `python scripts/validate_item_28b_decision_dossier.py`: four archived sources,
  ten mandatory tests, and four proposal-tamper probes pass.
- The validator reads the raw ZIP/XLSX rows, tariff extract, library HTML, open
  conflict records, and registry; it proves no Item 28B rule or interpretation
  has been registered.
- Stop for the project owner's explicit selection of `A_APPROVE_NARROW` or
  `B_DEFER`.

## 2026-08-04 — Item 28B narrow approval and draft registration

### Outcome

- The project owner explicitly agreed with recommended Alternative A. Recorded
  accepted Decision 0004 and immutable interpretation `INT-0002` with approval
  date, reviewer role, rationale, exact scope, exclusions, cited claims,
  authorized rules, and required regression tests.
- Registered reviewed Item 28B claims `CLM-0041`–`CLM-0043` and locators
  `LOC-0036`–`LOC-0038` for current tariff eligibility, exact 198.50 USD-per-
  occurrence rate, and archived row-24 fields.
- Registered draft package `2026.item-28b-extra-delivery.draft.1`, three draft
  rules, eleven source links, seven explicit dependencies, and three evidence
  requirements. All rules remain `not_implemented` and `draft`.
- Updated `CF-0001` and `CF-0003` with the narrow Item 28B exception while
  preserving both conflicts broadly. The original proposed dossier remains
  unchanged and separately verifiable.

### Verification and next

- Registry validation and all nine expected-invalid mutations pass.
- The Item 28B dossier validator proves the proposal/acceptance chain, raw
  sources, `INT-0002`, and the unpublished package gate; four tamper probes pass.
- Next, implement the Item 28B deterministic rating and all ten mandatory test
  classes. Only then may the draft rules/package be replaced by a published
  immutable version.

## 2026-08-04 — Published Item 28B deterministic rating

### Outcome

- Implemented the Decision 0004 / `INT-0002` Item 28B evaluator for domestic
  DP3 shipments. It selects the rate cycle from the actual pickup performance
  fact, counts only completed extra deliveries before final delivery, requires
  timely Destination-PPSO Government authorization and reviewed authorization/
  completion evidence, and multiplies exact occurrences by 198.50 USD using
  `Decimal` with no rounding.
- Added synthetic logical fixture `SYNTH-LS-011` plus 25 rating cases covering
  both effective boundaries, wrong-cycle blocks, requested-date isolation,
  absent/denied/malformed authorization, evidence gates, final-delivery
  exclusion, duplicates, exact two-occurrence arithmetic, units, chronology,
  provenance, and five result-tamper probes. No real shipment data was used.
- Promoted the approved draft to immutable published package
  `2026.item-28b-extra-delivery.1`; all three authorized rules are implemented
  and published. `CF-0001` and `CF-0003` remain open outside this narrow scope.
- Updated the shared logical-schema validator, fixture guide, schema conflict
  note, registry guide, and M3/M4 milestone status.

### Verification and next

- `python scripts/validate_item_28b_extra_delivery.py`: all 25 cases and five
  result-tamper probes pass.
- `python scripts/validate_logical_schema_fixtures.py`: all 11 positive scenarios
  and paired negative probes pass.
- Every repository `validate_*.py` suite passes; Python compilation and
  `git diff --check` pass.
- Next, add immutable Item 28B invoice/payment facts, deterministic post-audit
  reconciliation, and a second registered report adapter. Do not infer that the
  Item 28A audit mapping or invoice facts apply without an Item 28B contract.

## 2026-08-04 — Counsel billing-clarification brief

### Outcome

- Drafted a 521-word send-ready memo for the project owner's law-firm contact.
- Prioritized the three questions with the greatest cross-family leverage:
  currency of the 12 August 2022 domestic Item Code Listing, actual-versus-
  requested pickup rate-date selection, and the Item 4.5 reweigh 5,000-pound
  branch fact and exact boundaries.
- Requested governing artifacts with version, effective period, locator, and
  sanitized examples; distinguished published authority from customary
  practice and prohibited live personal or financial data.

### Verification and next

- Cross-checked every technical premise against the conflict register and
  monetary charge-family inventory. The brief contains 521 words and 74 source
  lines; no external message or data transfer occurred.
- Next, the owner can personalize and send the brief while Item 28B post-audit
  reconciliation proceeds independently.

## 2026-08-04 — Item 28B audit adapter and two-family report

### Outcome

- Added internal policy `AUDIT-DP3-ITEM-28B-RECONCILIATION-V1` and registered
  `CHARGE-ADAPTER-DP3-ITEM-28B-V1`. Matching requires raw `28B`, `EA`, accepted
  `INT-0002` mapping, reviewed immutable invoice/payment evidence, and complete
  histories through the cutoff.
- Extracted the existing occurrence-charge audit core into an explicit contract
  boundary. Item 28A retains its own policy, package, provenance, decision, and
  outputs; its complete prior regression suite remains unchanged.
- Added synthetic corrected Item 28B invoice/payment history and 23 audit cases
  covering billing, quantity, payment, missing/unsupported lines, mapping,
  completeness, evidence, chronology, malformed input, and seven result tampers.
- Added one shared synthetic shipment history with accepted Item 28A and Item
  28B lines and allocations. The closed report totals exactly 397.00 USD; the
  blocked case proves one family suppresses aggregate money without erasing the
  other family's decided findings.

### Verification and next

- All 16 `scripts/validate_*.py` suites pass. Logical-schema coverage is 12
  positive scenarios plus paired negative probes; audit-report coverage is six
  canonical cases plus ten output-tamper and three request-contract probes.
- Changed-module Python compilation and `git diff --check` pass. No real data,
  external write, live submission, or money movement was used.
- Next, send the counsel brief, register the response by authority type, and
  re-run readiness before selecting the reweigh fee or Item 130.

## 2026-08-04 — Post-Item-28B readiness refresh

### Objective

Re-run the deterministic monetary source-readiness gate after Item 28B approval,
rating publication, and audit-adapter completion so the next-family decision no
longer relies on the earlier blocked assessment.

### Outcome

- Published assessment `DP3-MONETARY-READINESS-2026-08-04-2`. Items 28A and 28B
  are unranked implemented references whose six gates cite `INT-0001` and
  `INT-0002`, their evidence contracts, archived sources, and audit support.
- Re-ranked the five still-blocked candidates. The Item 4 reweigh fee is rank
  one because it can reuse published weight/refund packages, but `CF-0004`,
  `CF-0001`, and `CF-0003` still prohibit money. Item 130 is rank two and remains
  the safe non-monetary fact-model fallback.
- Corrected the first-family inventory's current-status note without altering
  the historical selection result or broadening either scoped interpretation.
- Strengthened validation to bind the assessment ID and require every all-pass
  family to declare published-and-audited status.

### Verification and next

- `python scripts/validate_source_readiness_matrix.py`: seven candidates, 16
  provenance records, five blockers, and six tamper probes pass.
- `python scripts/validate_source_rule_registry.py`: the registry and all nine
  expected-invalid mutations pass.
- Next, register any counsel response and re-run the gate. If none is available,
  prepare an Item 130 fact-model decision package that publishes no money and
  preserves `CF-0001` and `CF-0003`.

## 2026-08-04 — Proposed Item 130 non-monetary fact-model dossier

### Objective and authority

Prepare the rank-two Item 130 fact/evidence model while the reweigh and current
item-code questions remain externally blocked. The project owner agreed that
this bounded work makes sense; no field-level or financial interpretation
approval was inferred.

### Source findings

- Re-read archived 400NG Item 130, pp. 54–55, and inspected all 66 candidate
  `DOM_400NG!A53:Q118` rows from the unchanged 12 August 2022 listing.
- Preserved four source gaps: tariff 130B includes riding lawnmowers absent from
  the rows; tariff 130E names more over-14-foot watercraft than rows 89–90; 130F
  directs boat trailers to BOTO while rows 91–92 present dHHG representations;
  and the tariff's combined loading/unloading charge does not silently collapse
  into the listing's separate origin/destination rows.
- Retained `CF-0001` and `CF-0003`. The listing values remain candidate future
  mapping evidence and are not treated as a current 2026 billing contract.

### Proposed contract

- Added Decision 0005 with seven proposed entities and 56 fields covering
  article identity/classification, exact measurements, conditional state,
  service context, immutable handling events, reviewed loading/unloading pairing
  candidates, and Government preapproval.
- Every field declares type, cardinality, evidence requirement, provenance, and
  interpretation status. Unknown/conflicting values and human review remain
  explicit; no real shipment fixture was created.
- Added 18 mandatory boundary tests spanning 130A–130J, measurement thresholds,
  exclusions, preapproval, Code 2/crating, hand-carry/carton exceptions, shuttle,
  SIT/TSP convenience, event pairing, source gaps, exact decimals, and the
  no-financial-output boundary.
- Alternative `A_APPROVE_FACT_MODEL_ONLY` would authorize synthetic schema
  fixtures and negative probes. `B_REVISE_FACT_MODEL` requests contract changes.
  Neither alternative registers an interpretation or authorizes money.

### Verification and next

- `python scripts/validate_item_130_fact_model_dossier.py`: seven entities, 56
  fields, four source gaps, 18 mandatory tests, and six tamper probes pass.
- The validator checks the archived tariff, a canonical hash of all 66 raw
  workbook rows, source versions, open conflicts, empty approval fields, absence
  of Item 130 registry packages/rules/decisions, and prohibited financial fields.
- Next, the owner reviews and explicitly selects `A_APPROVE_FACT_MODEL_ONLY` or
  `B_REVISE_FACT_MODEL`. Do not create the synthetic fixture before that review.

## 2026-08-04 — Item 130 fact-model revision after owner review

### Decision

- The project owner explicitly agreed with the architectural review and selected
  `B_REVISE_FACT_MODEL`, instructing the project to proceed.
- Recorded the accepted revision request separately from the unchanged version-1
  proposal. The decision is an internal schema-design review and creates no
  interpretation decision ID or financial authority.

### Revision

- Published a revised proposal that references the exact version-1 dossier by
  SHA-256 and inherits its sources, classifications, four source gaps, 18 test
  categories, open conflicts, exclusions, and no-money gate unchanged.
- Replaced seven Item 130-specific entity proposals with five new article-domain
  entities and two profiles of canonical `service_performance` and
  `service_approval_event` records. The revised design avoids duplicate sources
  of truth for handling and Government approval.
- Added 11 common identity, audit, provenance, sensitivity, sanitization,
  supersession, and correction fields. Status changes append or directly
  supersede prior records; current status is derived and no in-place update is
  allowed.
- The service-performance profile preserves an unmapped candidate family and
  prohibits `service_definition_id`, quantity, billing code, rate version, and
  amount while `CF-0001`/`CF-0003` remain open. The approval profile preserves
  raw approver text and prohibits a standardized Item 130 mapping.

### Verification and next

- `python scripts/validate_item_130_fact_model_dossier_v2.py`: five new
  entities/32 fields, two canonical profiles/19 fields, 11 common fields,
  preserved v1 source contract, and six architecture tamper probes pass.
- The probes reject a changed base hash, unapproved status, duplicate service
  entity, in-place status mutation, required mapped service definition, and
  inserted money.
- All 18 repository validators, changed-validator compilation, and `git diff
  --check` pass.
- Next, the owner reviews revised Alternative
  `A_APPROVE_REVISED_FACT_MODEL_ONLY` or requests `B_REVISE_AGAIN`. No logical-
  schema or fixture change is authorized before that review.

## 2026-08-04 — Item 130 revised fact model ratified and integrated

### Decision and boundary

- Recorded the project owner's explicit ratification of revised Alternative A
  in a separate approval record. This is an internal non-monetary schema-design
  approval and creates no interpretation decision or financial authority.
- Preserved `CF-0001`, `CF-0003`, all four tariff-versus-listing gaps, and the
  18-category boundary-test contract. The approval does not select a code,
  rate, unit, billable quantity, amount, or current Item 130 listing.

### Schema and first fixture

- Amended the logical schema with five append-only article-domain records and
  Item 130 profiles of canonical `service_performance` and
  `service_approval_event`. Unmapped candidate families and raw approver roles
  remain evidence-backed facts; financial use still requires a separately
  approved mapping and rule package.
- Added synthetic fixture `SYNTH-LS-013`, centered on the exact 250-cc 130B
  motorcycle boundary. It records classification, measurement, condition,
  context, planned/completed handling, preapproval, and a non-billable combined
  handling pair without any service definition, billing quantity, rate, amount,
  reconciliation, or payment fact.
- Extended the logical-schema validator for the ratified records, evidence
  targets, chronology, append-only correction semantics, and no-money gate.
  Five focused negative probes reject inserted money, premature service mapping,
  missing measurement evidence, self-supersession, and a 249-cc mutation.

### Verification and next

- `python scripts/validate_logical_schema_fixtures.py`: 13 synthetic scenarios
  pass; `SYNTH-LS-013` also rejects all five focused negative probes.
- The revised-dossier validator now requires the ratification record and still
  verifies the preserved version-1 source contract and architecture tamper
  probes.
- All 18 repository validators, changed-validator compilation, and `git diff
  --check` pass after integration.
- Next, expand the remaining ratified Item 130 non-monetary boundary fixtures.
  Do not implement a monetary rule, mapping, rate, quantity, or audit adapter
  unless the source conflicts close through a separate decision.

## 2026-08-04 — Item 130G television boundary fixture

### Outcome

- Added synthetic fixture `SYNTH-LS-014` for the ratified Item 130G boundary
  category. Three reviewed articles preserve an exact 48-inch non-flat positive
  candidate, a 47.999-inch non-flat below-threshold result, and an exact
  48-inch flat-screen exclusion.
- Each classification, exact decimal measurement, explicit inch unit, and
  flat-screen condition has an exact reviewed evidence target and full
  source/design provenance. Rejected articles carry no 130G candidate rather
  than an invented negative billing decision.
- The fixture contains no service performance, approval, pairing, billing
  mapping, quantity, rate, amount, rule, reconciliation, or audit output.

### Verification and next

- Extended the logical-schema validator with Item 130G invariants and five
  focused negative probes. They reject a changed positive threshold, automatic
  classification of either excluded article, missing classification evidence,
  and inserted money.
- `python scripts/validate_logical_schema_fixtures.py`: all 14 scenarios pass;
  both Item 130 fixtures reject their five focused probes.
- All 18 repository validators, changed-validator compilation, and `git diff
  --check` pass after adding the cluster.
- Next, implement the 130I/130J 100-cubic-foot and assembled-state boundary
  cluster under the same non-monetary and exact-evidence gate.

## 2026-08-04 — Item 130I/130J volume and assembly boundaries

### Outcome

- Added synthetic fixture `SYNTH-LS-015` for the ratified Item 130I/130J test
  category after rechecking the archived 400NG wording on page 55.
- Modeled six reviewed articles: a playhouse and hot tub each appear as an
  assembled 100.001-cubic-foot positive candidate, an assembled exact-
  100-cubic-foot rejection, and an over-100-cubic-foot disassembled rejection.
- Preserved volume as exact decimal strings with explicit `cu_ft` units and
  physical-dimensions methods. Article identity, volume, and moved-assembled
  state each have exact reviewed evidence targets and source/design provenance.
- No service performance, approval, pairing, billing mapping, quantity, rate,
  amount, rule, reconciliation, or audit output was added.

### Verification and next

- Extended the logical-schema validator with family-specific classification,
  strict-greater-than volume, assembled-state, evidence, and no-money
  invariants. Six focused mutations test both families and reject missing
  evidence and inserted money.
- `python scripts/validate_logical_schema_fixtures.py`: all 15 scenarios pass;
  `SYNTH-LS-015` rejects all six focused negative probes.
- All 18 repository validators, changed-validator compilation, and `git diff
  --check` pass after adding the cluster.
- Next, build the boat-focused 130C–130F measurement, associated-trailer,
  HHG-co-move, and BOTO/OTO boundary cluster without resolving the recorded
  130E/130F source gaps.

## 2026-08-04 — Cold-resume checkpoint

### Outcome

- Re-read `goal.md`, `state.md`, the active milestones in `plan.md`, and the
  latest worklog entries.
- Confirmed the working tree was clean and that `SYNTH-LS-015` is the last
  completed logical-schema fixture.
- Rechecked the archived 400NG Item 130 passage governing 130C–130F boat
  classifications, fractional-foot handling, measurement methods, associated
  trailers, HHG co-movement, and the separate OTO boundary.
- Made no schema, fixture, validator, mapping, rule, or financial change.

### Next

Add the synthetic 130C–130F boat boundary cluster and focused negative probes,
while preserving `GAP-130E-SUBTYPE-ROWS` and `GAP-130F-BOTO-BOUNDARY` as human-
review conflicts and emitting no monetary or billing-mapping output.

## 2026-08-04 — Item 130C–130F boat boundaries

### Outcome

- Added synthetic fixture `SYNTH-LS-016` with reviewed 130C canoe, jet-ski, and
  kayak candidates spanning absent, present, and unknown associated-trailer
  states; reviewed 130D/130E boat and dinghy candidates; and 130F boundary
  facts.
- Preserved exact decimal physical center-line, manufacturer length-overall,
  manufacturer center-line, physical width/height, and trailer measurements.
  The fixture proves that 14.999 and 16.999 feet exercise the tariff's
  fractional-foot treatment while exact 17 feet is not assigned 130F.
- Kept article classification separate from reviewed HHG co-move and domestic
  OTO/BOTO program context. The width probe uses 83 inches and the height fact
  uses the exact 77-inch boundary.
- Preserved `GAP-130E-SUBTYPE-ROWS` and `GAP-130F-BOTO-BOUNDARY` as explicit,
  provenance-linked open gaps. The 130F BOTO observation remains conflicting;
  no service mapping, quantity, rate, money, rule, reconciliation, or audit
  output was added.

### Verification and next

- `python scripts/validate_logical_schema_fixtures.py`: all 16 scenarios pass;
  `SYNTH-LS-016` rejects nine focused mutations covering length, method,
  trailer-state, classification, HHG/BOTO context, both source gaps, and money.
- All 18 repository validators, changed-validator compilation, and `git diff
  --check` pass.
- Next, add the ratified Item 130 exclusion and Government-approval boundary
  cluster, followed by handling/SIT pairing cases without financial outputs.

## 2026-08-04 — Item 130 exclusions and preapproval boundaries

### Outcome

- Added synthetic fixture `SYNTH-LS-017` with separate reviewed observations
  for Code 2, approval for crating, performed crating, one-person hand-carry,
  standard-carton transport, and completed shuttle transload.
- Preserved canoe, kayak, and dinghy as the three named exceptions to the
  hand-carry/carton exclusion; ordinary windsurfer facts exercise both exclusion
  paths without treating article classification as a financial decision.
- Added six isolated completed handling performances. A deterministic
  non-financial gate identifies timely approved reviewed preapproval as ready
  and keeps missing, denied, conflicting, late, and unreviewed evidence states
  distinct.
- Reused the ratified canonical service-performance and approval-event profiles.
  Service definitions, controlled approver roles, quantities, rates, money,
  rules, reconciliation, and audit outputs remain prohibited.

### Verification and next

- `python scripts/validate_logical_schema_fixtures.py`: all 17 scenarios pass;
  `SYNTH-LS-017` rejects twelve focused mutations covering exclusion collapse,
  named exceptions, shuttle state, approval status/timing/evidence, premature
  service mapping, and money.
- All 18 repository validators, changed-validator compilation, and `git diff
  --check` pass.
- Next, add zero/one/multiple/unmatched/duplicate handling pairs and the three
  SIT-cause states without deriving a billable quantity.

## 2026-08-04 — Item 130 handling and SIT pairing boundaries

### Outcome

- Committed the previously verified `SYNTH-LS-016` and `SYNTH-LS-017`
  checkpoint as `2e92d32` before beginning the next fixture.
- Added synthetic fixture `SYNTH-LS-018` with nine reviewed Item 130C article
  records. It distinguishes zero, one, two distinct, unmatched-loading,
  unmatched-unloading, and duplicate loading/unloading pairing states.
- Preserved duplicate pair references as two explicit `CONFLICTING` candidates;
  they do not become an accepted count. Accepted pairs require the same article,
  completed loading before unloading, reviewed evidence, and unique references.
- Added three SIT-linked factual pairs with separate `TSP_CONVENIENCE`,
  `NOT_TSP_CONVENIENCE`, and `UNKNOWN` cause observations. Pair acceptance only
  records the reviewed physical relationship and does not decide eligibility.
- Kept `GAP-130-COMBINED-VS-OD`, `CF-0001`, and `CF-0003` open. The fixture
  contains no service definition, billing mapping, quantity, rate, money, rule,
  reconciliation, payment, or audit output.

### Verification and next

- `python scripts/validate_logical_schema_fixtures.py`: all 18 scenarios pass;
  `SYNTH-LS-018` rejects twelve focused mutations covering pairing cardinality,
  article identity, duplicate conflict, SIT linkage/cause, evidence, the source
  gap, premature mapping, and inserted quantity.
- All 18 repository validators, changed-validator compilation, and `git diff
  --check` pass.
- Next, add the remaining 130A/130H and unlisted-similar-article boundary probes
  under the same reviewed-evidence and no-financial-output gate.

## 2026-08-07 — Item 130A/130H classification boundaries

### Outcome

- Added synthetic fixture `SYNTH-LS-019` after rechecking archived 400NG Item
  130A on page 54 and Item 130H on page 55. It preserves reviewed automobile,
  truck, van, baby grand piano, and grand piano facts as direct classification
  candidates.
- Recorded an upright piano as the tariff's express 130H exclusion. It remains
  a reviewed rejected fact with no classification candidate, proving that a
  similar article is not auto-classified.
- Every article has one exact reviewed evidence target plus source ID, document
  version, effective period, page locator, retrieval date, and interpretation
  status. No service mapping, quantity, rate, money, rule, reconciliation, or
  audit output was added.

### Verification and next

- `python scripts/validate_logical_schema_fixtures.py`: all 19 scenarios pass;
  `SYNTH-LS-019` rejects seven focused mutations covering classification drift,
  a missing positive candidate, upright-piano auto-classification/review drift,
  missing evidence, premature service mapping, and inserted money.
- All 18 repository validator scripts, changed-validator compilation, and `git
  diff --check` pass.
- Next, audit the completed Item 130 fixtures against all 18 ratified mandatory
  test categories and identify any remaining non-monetary coverage gap.

## 2026-08-07 — Item 130 mandatory-test coverage audit

### Outcome

- Added audit `ITEM-130-MANDATORY-COVERAGE-2026-08-07-1`, binding the exact 18
  inherited and ratified Decision 0005 categories, seven Item 130 fixtures, and
  three existing validator artifacts by SHA-256.
- Classified 16 categories as `COVERED`, two as `PARTIAL`, and none as missing.
  Added a human-readable companion table without changing Item 130 financial or
  mapping authority.
- Recorded `GAP-130-TEST-POSITIVE-CORRECTION-CHAIN`: exact decimals, units,
  evidence targets, append-only schema semantics, and malformed self-
  supersession are tested, but no valid positive Item 130 correction chain is
  exercised.
- Recorded `GAP-130-TEST-FORBIDDEN-FIELD-ALIASES`: dossier and registry gates
  remain intact, but the current fixture validators accept `rate_date_role` and
  `quantity_for_billing`. The audit validator reproduces both accepted aliases.

### Verification and next

- `python scripts/validate_item_130_coverage_audit.py`: 16 covered, two partial,
  zero missing, two reproduced gaps, and six audit-record tamper probes pass.
- All 19 repository validator scripts, changed-module compilation, and `git
  diff --check` pass.
- Next, close only the positive correction-chain gap with a valid direct
  supersession and malformed-correction probes. The forbidden-field alias gap
  remains a separate subsequent outcome.

## 2026-08-07 — Item 130 positive correction chain

### Outcome

- Closed `GAP-130-TEST-POSITIVE-CORRECTION-CHAIN` by revising `SYNTH-LS-013` to
  preserve an original reviewed 249-cc motorcycle specification and a later
  reviewed 250-cc correction.
- The correction directly supersedes the original observation, retains the same
  article and physical observation time, records a nonempty reason later in
  time, and uses a separately superseding document version and separately
  targeted reviewed evidence. Both values remain exact decimal strings with an
  explicit `cc` unit.
- Expanded the focused `SYNTH-LS-013` mutations from five to ten. They reject
  missing correction evidence, 249-cc current-value drift, missing/self-
  referential supersession, missing reason, non-later recording, changed stable
  subject, inserted money, premature mapping, and invalid pair self-
  supersession.
- Preserved coverage audit version 1 unchanged by SHA-256 and published version
  2 as an explicit superseding assessment. Current coverage is 17 covered, one
  partial, and zero missing; financial authority remains prohibited.

### Verification and next

- `python scripts/validate_logical_schema_fixtures.py`: all 19 scenarios pass;
  `SYNTH-LS-013` rejects all ten focused mutations.
- `python scripts/validate_item_130_coverage_audit.py`: version-1 history,
  version-2 correction closure, the one remaining alias gap, and six tamper
  probes pass.
- All 19 repository validator scripts, changed-module compilation, and `git
  diff --check` pass.
- Next, close only `GAP-130-TEST-FORBIDDEN-FIELD-ALIASES` with a shared recursive
  forbidden-output guard and focused rate-date/billing-quantity alias probes.

## 2026-08-07 — Item 130 forbidden-output guard and 18/18 coverage

### Outcome

- Closed `GAP-130-TEST-FORBIDDEN-FIELD-ALIASES` with a shared recursive guard
  invoked before every Item 130 scenario-specific validator. It scans all nested
  fixture records and normalizes field names to lowercase alphanumeric form.
- The guard rejects 50 canonical billing-mapping, quantity, rate-date, rate,
  money, rule-package, reconciliation, and audit-output keys while leaving
  reviewed non-monetary candidate facts and unmapped profiles intact.
- Added six shared mutations covering `rate_date_role`,
  `quantity_for_billing`, camel-case variants, and nested `rate-date` and
  `expectedAmount` fields. All six are rejected through the shared guard.
- Preserved coverage-audit versions 1 and 2 unchanged by SHA-256 and published
  version 3. All 18 mandatory categories are now covered; no test gap remains.
  Four Item 130 source gaps and `CF-0001`/`CF-0003` remain open, and financial
  authority is explicitly unchanged and prohibited.

### Verification and next

- `python scripts/validate_logical_schema_fixtures.py`: all 19 scenarios, 61
  family-specific Item 130 probes, and six shared forbidden-output probes pass.
- `python scripts/validate_item_130_coverage_audit.py`: 18 covered, zero partial,
  zero missing, immutable version-1/version-2 history, six forbidden-output
  probes, and six audit tamper probes pass.
- All 19 repository validator scripts, changed-module compilation, and `git
  diff --check` pass.
- The bounded public-source non-monetary Item 130 synthetic verifier is complete.
  Next progress depends on authoritative source clarification; do not implement
  Item 130 mapping, quantity, money, rules, or audit adapters from this result.

## 2026-08-07 — Historical acceptance pipeline operational

### Outcome

- Added the versioned historical-acceptance policy and deterministic pipeline.
  An executable case now supplies source-structured rating facts, shared
  invoice/payment evidence, intake controls, and a separately authored expected
  projection. The pipeline executes registered rating packages and audit
  adapters before comparing the result with that fixed projection.
- Defined three non-interchangeable corpus tiers. Source-structured synthetic
  cases are executable benchmarks, public precedents are reference-only, and
  only written-authorized, pre-ingest-sanitized, independently expert-labeled
  historical cases may count toward the ratified 25.
- Added one two-family synthetic bundle that executes Items 28A and 28B through
  exact rating, reconciliation, combined reporting, and expected-outcome
  comparison. Its exact USD 397.00 result matches, but it remains non-counting.
- Recorded official GAO page B-199780 as a URL-only public candidate. It remains
  `PENDING_AUTHORITATIVE_ARCHIVE`; no decision text, real shipment content, or
  extracted claim was stored or treated as a permanent source.
- Added recursive sensitive-field rejection, authorization and sanitization
  gates, independent-label chronology, exact corpus counts, canonical JSON,
  mismatch paths, and altered-report rejection. The corpus reports
  `OPERATIONAL` and completion `NOT_READY`, with 25 passing historical cases
  still required.

### Verification and next

- `python scripts/validate_historical_acceptance_pipeline.py`: two corpus
  records, 11 request-gate probes, one independent-outcome mismatch probe, and
  eight report-tamper probes pass.
- All 20 repository validators, changed-module compilation, and `git diff
  --check` pass.
- Next, archive an authoritative public decision artifact before extracting a
  sanitized precedent, then add further source-structured discrepancy and
  human-review benchmark bundles. No real case may be loaded without written
  authorization and verified pre-ingest sanitization.

## 2026-08-07 — First public precedent archived and sanitized

### Outcome

- Archived the official three-page `SRC-CBCA-1536-RELO-2009` decision PDF
  unchanged at 113,298 bytes with SHA-256
  `27d847b1c9200d3740b32a67e1c0598da66904b2d77618f6d20b5b0eddf65071`.
  PDF signature, metadata, text extraction, and all three 144-DPI page renders
  were checked.
- Added a separately checksummed sanitized JSON extract. It removes personal,
  location, agency, carrier, shipment-identifier, and signature identity data;
  preserves exact decimal strings and units for the adjudicated facts; and
  labels the decision federal-civilian, non-DP3, out-of-scope context only.
- Registered the immutable raw artifact in the source manifest and physical
  source registry. The acceptance fixture now records both repository-relative
  paths, both SHA-256 values, its extraction method, and complete provenance.
- Closed the archived-public-record projection gap: an archived precedent now
  retains its artifact lineage in validated report output. The validator checks
  the PDF signature, raw and derived hashes, manifest join, sanitization label,
  and non-DP3 scope before execution.
- The precedent remains `REGISTERED_REFERENCE_ONLY`, is never executed as a
  current 400NG case, and does not count toward the required 25. Current
  acceptance counts remain zero passing authorized historical cases and 25
  remaining.
- Attempts to archive the previously identified GAO candidate from its official
  product and asset endpoints returned HTTP 403. No GAO text or search snippet
  was promoted to the permanent source record; the downloadable CBCA artifact
  supplies the first operational public-precedent archive instead.

### Verification and next

- `python scripts/validate_historical_acceptance_pipeline.py`: one passing
  synthetic benchmark, one archived reference-only precedent, 11 request gates,
  one independent-outcome mismatch probe, and eight report-tamper probes pass.
- `python scripts/validate_source_rule_registry.py`: all eleven physical source
  versions match the manifest and all registry cases pass.
- All 20 repository validators, changed-module compilation, and `git diff
  --check` pass.
- Next, add separately labeled synthetic discrepancy and human-review bundles.
  Continue pursuing written authorization and verified pre-ingest sanitization
  before any real historical case enters the environment.

## 2026-08-07 — Opposing-discrepancy acceptance benchmark

### Outcome

- Added `ACCEPT-SYNTH-28A-28B-002-DISCREPANCY`, a second independently labeled
  source-structured synthetic benchmark that reuses the registered Item 28A and
  Item 28B rating and audit adapters.
- The synthetic invoice deliberately bills Item 28A at USD 250.00 against USD
  198.50 expected and Item 28B at USD 150.00 against USD 198.50 expected. The
  report preserves the USD 51.50 overbilling and USD 48.50 underbilling as two
  open line findings even though the aggregate billing variance nets to only USD
  3.00. Expected, invoiced, and paid totals are exactly USD 397.00, USD 400.00,
  and USD 400.00.
- Added bounded fixture assembly for exact audit-record mutations. Mutation
  paths must remain under `records`, must be unique, and must provide explicit
  values; path escape and duplicate-path probes are rejected before execution.
- Extended the independent-label regression check to alter a discrepancy line's
  labeled amount. The mismatch is reported at the exact projection path while
  the deterministic USD 400.00 financial output remains unchanged.
- Both synthetic benchmarks pass their independently authored labels, require
  the correct clean/open review behavior, remain acceptance-ineligible, and add
  zero cases to the required 25.

### Verification and next

- `python scripts/validate_historical_acceptance_pipeline.py`: three corpus
  records, two assembly gates, 11 request gates, two independent-label mismatch
  probes, and eight report-tamper probes pass.
- All 20 repository validators, changed-module compilation, and `git diff
  --check` pass.
- Next, add one source-structured expected human-review benchmark in which a
  missing or conflicting evidence condition blocks a charge and suppresses all
  aggregate monetary totals without erasing decided charge-level results.

## 2026-08-07 — Evidence-blocked human-review acceptance benchmark

### Outcome

- Added `ACCEPT-SYNTH-28A-28B-003-EVIDENCE-BLOCKED`, a third independently
  labeled source-structured synthetic benchmark. Item 28A remains final and
  correctly billed at USD 198.50; Item 28B blocks on
  `INVOICE_LINE_EVIDENCE_MISSING_OR_UNREVIEWED:LINEV-MULTI-28B`.
- Verified all-or-nothing report behavior. The blocked report preserves the
  decided Item 28A result and the exact Item 28B blocker, reports one final and
  one blocked charge, requires human review, and exposes no aggregate currency,
  amounts, or variances.
- The first shared-record mutation correctly caused both adapters to distrust
  the invoice. To express the intended charge-specific review state, versioned
  the historical-acceptance policy to `2026-08-07.2` and added an explicit
  provenance-complete charge-scoped audit record projection. Historical source
  mutation remains prohibited; the bounded mutation mechanism is synthetic
  fixture assembly only.
- Added charge-scoped assembly gates for paths outside `records` and duplicate
  paths, plus a request gate rejecting non-object charge audit records.
- Added a blocked-label mismatch probe. Changing the independently authored
  blocked reason produces an exact mismatch path without changing the
  deterministic blocked result or exposing aggregate money.
- Added report tamper rejection for injected aggregate money on a blocked
  report. All three synthetic benchmarks remain acceptance-ineligible and
  contribute zero cases to the required 25.

### Verification and next

- `python scripts/validate_historical_acceptance_pipeline.py`: four corpus
  records, four fixture-assembly gates, 12 request gates, three independent-label
  mismatch probes, and nine report-tamper probes pass.
- All 20 repository validators, changed-module compilation, and `git diff
  --check` pass.
- Clean, decided-discrepancy, and evidence-blocked acceptance paths are now
  operational. Next, define and validate the metadata-only authorization and
  pre-ingest sanitization intake contract needed before any real historical case
  can enter the environment.

## 2026-08-07 — Metadata-only historical intake control

### Outcome

- Published `HISTORICAL-INTAKE-CONTROL-V1` version `2026-08-07.1` and
  historical-acceptance policy version `2026-08-07.3`. The exact-field envelope
  contains control metadata only and cannot carry shipment content.
- Added deterministic gates for current written-authorization metadata, exact
  domestic DP3 post-audit scope, independent verification, sanitization method
  and bundle SHA-256, authorization-before-sanitization and
  sanitization-before-ingest chronology, raw-source exclusion, hidden-metadata
  removal, prohibited-category completeness, retention, provenance, and four
  distinct critical approval roles. AI attestation is prohibited.
- Added one explicitly non-authorizing `SYNTHETIC_TEMPLATE`. It is labeled
  synthetic metadata-only, carries no real case or authority, sets real-data
  ingest authority false, and is rejected by the operational validator.
- Added 16 metadata-only negative mutations covering missing and stale
  authorization, contradictory authority, self-attestation, premature ingest,
  raw-source exposure, hidden metadata, incomplete removed categories,
  sanitizer self-review, expired retention, AI attestation, case-content
  presence, template promotion, duplicated critical roles, malformed bundle
  hash, and incomplete provenance. An additional exact-schema gate rejects an
  injected case-content field.
- Integrated the operational envelope into the
  `AUTHORIZED_SANITIZED_HISTORICAL` tier. The envelope authorization reference
  must match the intake record and its outcome-reviewer role must match the
  independent expert label. Synthetic cases are forbidden from carrying the
  envelope; a historical-tier request without one is rejected.
- No operational positive envelope or historical case was created. That remains
  blocked on actual written authorization and an approved sanitization process.

### Verification and next

- `python scripts/validate_historical_intake_control.py`: one non-authorizing
  template, 16 negative mutations, one operational-promotion gate, and one
  extra-field gate pass.
- `python scripts/validate_historical_acceptance_pipeline.py`: four corpus
  records, four assembly gates, 14 request gates, three label-mismatch probes,
  and nine report-tamper probes pass.
- All 21 repository validators, changed-module compilation, and `git diff
  --check` pass.
- Next, create a no-data onboarding runbook and empty corpus-manifest contract
  that tells an authorized data owner exactly what approvals, sanitized
  artifacts, hashes, reviewers, and handoff evidence are required. Do not
  populate it until separate written authorization exists.

## 2026-08-07 — Empty historical corpus manifest and onboarding contract

### Outcome

- Published `HISTORICAL-CORPUS-MANIFEST-V1` version `2026-08-07.1` and a
  no-data onboarding runbook. The checked-in manifest is metadata-only, has no
  entries or ingest authority, and deterministically evaluates to zero passing
  historical cases with 25 remaining.
- Added exact-field validation for scope, provenance, canonical entry order,
  immutable contiguous versions, direct supersession, unique entry and
  case-version identities, and cross-case reuse of envelope, bundle, label, or
  report artifacts. Current versions alone contribute to derived counts.
- Prohibited caller-declared pass counts. Executed operational statuses require
  an acceptance-report ID and SHA-256; unexecuted and synthetic entries cannot
  carry that link.
- Added a visibly synthetic, non-authorizing two-version manifest chain. It
  links to the validated synthetic intake-envelope ID/hash and sanitized-bundle
  hash, confirms the intake contract's role-separation and no-AI-attestation
  controls, and remains non-counting.
- Added 16 negative mutations and eight structural/linkage gates covering
  count drift, content and authority contradictions, scope drift, duplicates,
  skipped or broken supersession, missing links, malformed hashes, promotion,
  future registration, provenance, caller-supplied passing counts, extra case
  content, synthetic report links, canonical order, populated empty mode, and
  cross-case artifact reuse.
- No operational manifest example, historical case, acceptance report, or real
  data was created.

### Verification and next

- `python scripts/validate_historical_corpus_manifest.py`: one immutable empty
  manifest, one non-counting two-version synthetic chain, 16 negative
  mutations, and eight structural/linkage gates pass.
- All 22 repository validators, changed-module compilation, and `git diff
  --check` pass.
- Next, add a deterministic no-data preflight/readiness result that converts
  the empty manifest and onboarding requirements into explicit external
  blockers. Do not create an operational envelope or populate the manifest
  without separate written authorization and an approved sanitization process.

## 2026-08-07 — Deterministic no-data historical readiness preflight

### Outcome

- Published `HISTORICAL-CORPUS-NO-DATA-PREFLIGHT-V1` version `2026-08-07.1`.
  It accepts only the authoritative `EMPTY_AWAITING_AUTHORIZATION` manifest and
  cannot authorize ingest, carry case content, register a case, satisfy a
  control, or create a historical pass.
- Added a canonical readiness report linked to the manifest ID, policy version,
  cutoff, and SHA-256. It reports `BLOCKED_EXTERNAL_PREREQUISITES`, zero of 25
  passing historical cases, 25 remaining, and eight ordered provenance-backed
  blockers covering authorization, sanitization, independent review, intake,
  expected labels, case registration, acceptance execution, and the completion
  deficit.
- Added presentation-neutral display fields for a future read-only operator
  surface: title, headline, progress label, primary action, and blocker count.
  The graphical interface seed is recorded in `plan.md`; no framework or UI was
  selected and no control logic moved into presentation.
- Added a read-only CLI that prints the current preflight as formatted JSON.
- Added 12 tamper probes for schema/policy drift, false readiness or authority,
  content insertion, fabricated counts, hidden deficit, false blocker
  satisfaction, contradictory display text, and manifest-hash tampering. Three
  structural gates reject overrides and missing/reordered blockers; two input
  gates reject synthetic and content-bearing manifests.
- No real data, operational intake envelope, operational manifest entry, or
  historical acceptance execution report was created.

### Verification and next

- `python scripts/validate_historical_corpus_preflight.py`: one canonical
  blocked report, 12 tamper probes, three structural gates, and two unsafe-input
  gates pass.
- `python scripts/show_historical_corpus_preflight.py` prints the deterministic
  zero-of-25 report for inspection.
- All 23 repository validators, changed-module compilation, and `git diff
  --check` pass.
- Next, define a metadata-only independent expected-label approval contract and
  cross-link it to the intake and manifest controls using non-authorizing
  synthetic metadata only. Do not create an operational label or outcome
  without the separately authorized sanitized corpus.

## 2026-08-07 — Metadata-only historical expected-label approval control

### Outcome

- Published `HISTORICAL-EXPECTED-LABEL-CONTROL-V1` version `2026-08-07.1`.
  Its exact-field envelope contains only control metadata and never embeds the
  expected projection, outcome, shipment facts, invoice facts, money, evidence
  documents, or label artifact.
- Added deterministic validation for the intake-envelope ID and canonical
  SHA-256, sanitized-bundle SHA-256, opaque case reference, label ID and
  SHA-256, post-ingest authorship, independent expert approval, pre-execution
  chronology, provenance, and explicit no-AI-authorship/no-AI-attestation
  boundaries.
- Enforced role separation between label author and reviewer, between the author
  and three critical intake approvers, and between the reviewer and those same
  intake approvers. The label reviewer must match the outcome-reviewer role
  reserved by the validated intake envelope.
- Added one explicitly non-authorizing `SYNTHETIC_TEMPLATE`. It uses a label-
  hash placeholder with no artifact, contains no case or outcome content, sets
  label-use authority false, records acceptance execution as not started, and
  is rejected by the operational gate.
- Cross-checked the template against the existing synthetic intake and corpus-
  manifest fixtures: case, intake ID/hash, bundle hash, label ID/hash, and
  reviewer role all match.
- Added 20 negative mutations for identity, hashes, content, authority, mode,
  case linkage, AI use, role separation, chronology, execution state, and
  provenance. Six additional gates reject embedded projection, money, shipment
  identifiers, a mismatched intake case, unsafe intake, and intake role
  conflicts.
- No operational label, expected-outcome artifact, real case, or historical
  acceptance execution was created.

### Verification and next

- `python scripts/validate_historical_expected_label_control.py`: one non-
  authorizing template, 20 negative mutations, one operational-promotion gate,
  and six content/intake-link gates pass.
- All 24 repository validators, changed-module compilation, and `git diff
  --check` pass.
- Next, move the intake/label/manifest cross-check from a test assertion into a
  reusable deterministic handoff verifier that reports registration readiness.
  Keep its synthetic result non-authorizing and non-counting.

## 2026-08-07 — Deterministic historical control handoff

### Outcome

- Published `HISTORICAL-CONTROL-HANDOFF-V1` version `2026-08-07.1`. The builder
  validates the intake envelope, expected-label approval control, and corpus
  manifest under their own policies, selects the single current entry for the
  opaque case, and verifies the complete pre-execution chain.
- Added exact cross-control checks for control mode, case reference, evaluation
  cutoff, intake-envelope ID/hash, sanitized-bundle hash, label ID/hash,
  current manifest entry/version/status, label-approval-before-registration,
  and absence of an acceptance-report link.
- The canonical synthetic result is
  `SYNTHETIC_LINKS_VERIFIED_NON_OPERATIONAL`: linkage is verified while
  operational readiness, execution authority, and count eligibility remain
  false. Four provenance-backed blockers preserve the synthetic intake, label,
  manifest, and 25-case boundaries.
- Added a presentation-neutral read model with linked-control identities and
  hashes, zero-of-25 progress, headline, primary action, and blocker list, plus
  a read-only JSON inspection command.
- Added 12 report-tamper probes, three report-structure gates, nine linked-input
  gates, and one operational-promotion gate. They reject false readiness,
  authority, counts, content, removed/reordered blockers, hash drift, label
  drift, pre-approval registration, cutoff mismatch, empty manifests, unsafe
  intake, and outcome-bearing controls.
- Hardened the corpus manifest so successor entry registration times cannot
  precede predecessor registration. A seventeenth manifest mutation protects
  that immutable-version chronology independently from the handoff's label-
  approval chronology.
- No operational intake, label, manifest entry, handoff, case data, or
  historical acceptance execution was created.

### Verification and next

- `python scripts/validate_historical_control_handoff.py`: one canonical
  synthetic report, 12 tamper probes, three report-structure gates, nine
  linked-input gates, and one operational-promotion gate pass.
- `python scripts/show_historical_control_handoff.py` prints the deterministic
  linked-control read model.
- `python scripts/validate_historical_corpus_manifest.py`: 17 negative
  mutations and eight structural/linkage gates pass.
- All 25 repository validators, changed-module compilation, and `git diff
  --check` pass.
- The safe no-data M6 control chain now reaches a real external boundary.
  Resume the rank-one M1 source task: seek authoritative resolution of
  `CF-0004` without promoting search snippets or inaccessible observations.
