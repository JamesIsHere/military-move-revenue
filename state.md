# Current State

## Status

Active. The outcome, first user, completion test, public-source strategy, and
TSP-to-government domestic DP3 scope are ratified in `goal.md`.

## Active milestone

M1 — Establish the source foundation. M2 schema work is advancing in parallel
where it does not depend on the unresolved source-version questions.

## Completed

- Selected a read-only post-audit wedge.
- Selected domestic DP3 and TSP-to-government billing for version one.
- Defined a 25-case historical completion verifier.
- Agreed to proceed with public sources and synthetic cases while the user pursues
  authorized sanitized historical files separately.
- Identified the initial categories of authoritative sources.
- Ratified `goal.md` on 2026-08-03.
- Archived and checksummed nine core public source artifacts.
- Reviewed selected 400NG, TPPS, and Tender of Service pages visually and through
  text extraction.
- Established the first 71 reviewed/provisional source-to-field discoveries and
  a provisional conceptual model.
- Reformatted schema discoveries into narrow source indexes and mapping lists for
  readable plain-text editing.
- Reviewed Chapter A-402 shipment-date, arrival, delivery, partial-delivery, SIT,
  operational-gate, and status-history sections against rendered PDF pages.
- Modeled SIT as a versioned lifecycle episode, including split portions,
  approvals, control identifiers, extensions, releases, and conversion.
- Reconciled 400NG Items 17, 185, and 210 plus Appendix A against the Chapter
  A-402 SIT model and added ten reviewed discoveries (`DISC-0072`–`DISC-0081`).
- Separated SIT rating geography from the physical storage location and modeled
  charge-specific accrual, weight-basis, effective-date, and evidence decisions.
- Inspected all four archived P0 workbook families with the explicitly authorized
  openpyxl read-only fallback and created a reproducible structural extract.
- Added workbook-backed rate, item-code, transit, mileage, and SIT discoveries
  `DISC-0082`–`DISC-0091`; the discovery inventory now contains 91 entries.
- Recorded rather than resolved the tariff/rate-workbook date conflict, the
  current-transit/mileage-tool conflict, and item-code supersession uncertainty.
- Accepted a question-specific source-precedence and conflict-handling policy in
  Decision 0002.
- Registered three active interpretation cases containing six preserved source
  claims, interim behavior, closure evidence, and affected discoveries.
- Added source-claim, conflict-case, and interpretation-decision concepts to the
  provisional conceptual schema.
- Drafted the implementation-neutral logical schema across all 91 discoveries,
  including logical types, units, cardinality/nullability, validation,
  sensitivity, provenance, immutable versioning, and a logical ER map.
- Defined exact-decimal rating, expected-charge, reconciliation, finding, and
  human-review records while explicitly gating all three unresolved conflicts.
- Structurally verified the logical-schema document and corrected its initial
  omission of the first nine DD Form 619 discoveries.
- Added four explicitly synthetic logical-schema scenarios: straight-through,
  split SIT, correction history, and conflict-gated rating.
- Added executable validation of exact decimals, explicit units, provenance,
  references, invoice/payment balance, calculation steps, split-SIT boundaries,
  immutable corrections, late status receipt, and conflict gating.
- Tightened conditional cardinalities for blocked rule outcomes, unknown
  eligibility booleans, unrated audit amounts, and declared portion-weight units.
- Verified all four valid scenarios and four deliberately invalid regression
  probes.
- Researched current publication evidence for the Item Code Listing and
  mileage/transit/SIT tool across the legacy USTRANSCOM library, the new PPA
  resource center, current DTR text, and PPA advisories.
- Established from archived XLSX core properties that the mileage/SIT tool was
  last modified on 2025-09-26, before the 2026 transit table publication; this is
  a version marker, not an effective period.
- Narrowed CF-0002: the explicit 2026 table is the provisional domestic transit
  source, but the 70-percent authorized-SIT-day expression remains unsupported.
- Upgraded CF-0003 to a disputed publication-location gap because the 2026 400NG
  points to the legacy listing while PPA Advisory 26-0105 identifies the new PPA
  site as authoritative and its catalog does not expose that listing.
- Added six source claims (`CLM-0007`–`CLM-0012`) and a dedicated
  source-currency research record with archive limitations.

## Current task

Prepare the first conflict-aware physical source/rule registry increment from
the archived, reviewed subset. It must preserve candidate PPA publication
observations without allowing CF-0001, CF-0002, or CF-0003 to publish affected
rules.

## Known blockers

M1 source closure is externally constrained: PPA.mil and media.defense.gov
returned HTTP 403 to direct archival requests, the in-app browser was unavailable,
and the public record located so far does not state the mileage tool's effective
period, the referenced SIT percentage, or a complete current domestic item-code
supersession chain. Closure requires downloadable public artifacts, user-supplied
copies of those public files, or publisher clarification. Production
implementation of affected rate-date, authorized-SIT-day, and billing-code rules
remains blocked. Final acceptance also depends on authorized historical cases.

## Decisions needed

- Resolve the baseline-workbook banner versus 400NG Item 1.2(c) date-selection
  conflict before implementing SIT/accessorial rate selection.
- Establish the effective version of the mileage/SIT tool and the continued
  applicability or supersession of the 2022 item-code listing.
- Later: choose the initial subset of 400NG charge families for implementation.
- After synthetic schema validation: choose physical database and EDI boundary
  types without weakening the logical contract.

## Next three actions

1. Obtain and checksum the PPA-linked mileage/SIT workbook and Advisory 26-0105
   through an accessible public path or user-supplied public copies; compare the
   workbook hash to the archived USTRANSCOM copy.
2. Specify and implement the first physical source/rule registry from the
   conflict-free subset, with automated provenance and conflict-gate validation.
3. Expand synthetic validation when new source-backed conditional rules or EDI
   constraints are added; keep disputed behavior conflict-gated.

## Verification status

Goal ratified; source manifest, 91 contiguous source-to-field discoveries,
workbook inspection records, accepted source-precedence policy, three registered
conflict cases containing 12 preserved claims, conceptual schema, and a 442-line
logical schema exist. The logical schema's section set, Markdown table shapes,
Mermaid fence balance,
discovery-range coverage, and conflict gates passed structural checks. Four
synthetic scenarios plus four negative probes pass
`python scripts/validate_logical_schema_fixtures.py`; this is logical-contract
validation, not tariff-rule approval. PDF findings were visually checked;
workbook findings were structurally checked at the cell/formula level because no
rendering engine was available. The workbook extract now preserves raw core
properties; all four raw workbook hashes still match the manifest. PPA
publication evidence is documented but remains candidate because CDN restrictions
prevented raw archival. Executable tariff rules and a physical database schema do
not exist yet.
