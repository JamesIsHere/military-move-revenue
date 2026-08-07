# Plan

## M0 — Ratify the product contract

Status: complete on 2026-08-03.

Exit criteria:

- `goal.md` has been red-penned and explicitly ratified.
- The first user, financial relationship, program, completion verifier, and
  exclusions are unambiguous.

## M1 — Establish the source foundation

Status: in progress; public archival gaps remain for the current PPA artifacts
and disputed source-version questions.

Exit criteria:

- Mandatory public sources are downloaded and checksummed.
- Every source has authority, scope, version, effective dates, supersession,
  retrieval, and extraction status.
- Governing and contextual sources are clearly separated.
- Source precedence and conflict-handling policy are documented.

## M2 — Derive the canonical schema

Status: complete on 2026-08-03 for the public-source logical contract and
synthetic verifier; authorized historical cases may still refine it later.

Exit criteria:

- A source-to-field matrix covers shipment, party, location, weight, service,
  evidence, invoice, payment, rule, rate, and workflow concepts.
- Each field has a logical type, unit, cardinality, nullability rationale,
  sensitivity classification, validation, and provenance.
- Conceptual and logical ER diagrams exist.
- Unresolved domain questions are explicit.
- The schema is tested with synthetic straight-through and boundary cases.

## M3 — Implement the source and rule registry

Status: in progress. The first file-backed physical registry and conflict-gate
validator were implemented on 2026-08-03. Seven immutable reference/workflow
packages and two monetary packages are now published and executable: initial
weight, Item 4.8 automatic
reweigh, completed-reweigh net selection, initial-versus-reweigh lower
selection, constructive weight, containerized provisional weight, and
post-invoice reweigh refund workflow. Decision 0003 / `INT-0001` now approves a
2026 Item 28A-only source contract from the archived tariff, rate cells,
item-code row, and current public-library snapshot while leaving `CF-0003` open
for all broader item-code uses. The published Item 28A package implements that
narrow decision with exact-decimal rating and evidence gates. Decision 0004 /
`INT-0002` similarly approves and the registry publishes the scoped 2026 Item
28B extra-delivery package without resolving broader `CF-0003` applicability.

Exit criteria:

- Source artifacts and versions can be registered immutably.
- Rules and rates reference precise source locations and effective periods.
- Supersession is explicit and historical versions remain reproducible.
- Automated validation rejects incomplete provenance.

## M4 — Implement shadow rating

Status: in progress. `2026.item-28a-extra-pickup.1` and
`2026.item-28b-extra-delivery.1` are published monetary packages. Item 28A's 24
synthetic cases and five result-tamper probes pass; Item 28B's 25 synthetic cases
and five result-tamper probes pass. Other candidate monetary families remain
deferred by recorded source conflicts or larger fact-model requirements.

Exit criteria:

- Structured shipment facts can be entered without document extraction.
- A prioritized subset of domestic 400NG charges is calculated deterministically.
- Every result reports inputs, math, source, and evidence expectations.
- Synthetic boundary tests pass.

## M5 — Add evidence and post-audit comparison

Status: in progress. Item 28A and Item 28B now have deterministic audit slices:
immutable corrected invoice/payment histories, reviewed completeness and source-
evidence gates, exact expected/invoiced/paid variances, decided finding
classifications, and human-review blocks. Both registered adapters run together
against one shared synthetic shipment history with exact aggregate totals and
all-or-nothing blocking. Authorized historical data is not yet available.

Exit criteria:

- Evidence requirements attach to charge decisions.
- Expected, invoiced, and paid lines can be reconciled without loss of history.
- Missing, conflicting, and unsupported facts enter human-review queues.

## M6 — Historical acceptance

Status: in progress. The acceptance pipeline contract is operational for
clean, opposing-discrepancy, and evidence-blocked source-structured synthetic
benchmarks, archived public-precedent intake, and a non-authorizing metadata-only
historical intake-control template. A checked-in metadata-only corpus manifest
now provides the immutable empty landing state and a validated synthetic-only
entry/supersession contract.
It executes registered rating and audit adapters, compares an independently
authored expected-outcome projection, enforces authorization/sanitization gates,
derives corpus counts without accepting caller-declared passes, and keeps
non-historical tiers out of the required 25-case count. No authorized historical
case is loaded; the manifest evaluates to zero passing cases with 25 remaining.
A deterministic no-data preflight now exposes that state as eight provenance-
linked blockers plus presentation-neutral progress and action fields. A
metadata-only expected-label approval contract now validates the intake, bundle,
case, label-hash, independent-role, and pre-execution links using a synthetic
non-authorizing template. A reusable control-handoff verifier now validates that
envelope, the intake control, and the current manifest entry together and emits
a presentation-neutral blocked result. No operational expected label or handoff
exists.

Exit criteria:

- At least 25 authorized sanitized cases are loaded through an approved process.
- Expert-approved outcomes are independently recorded.
- The completion verifier in `goal.md` passes or discrepancies are documented.
- Security, sanitization, and retention controls are reviewed.

## Future interface seed — Operator review surface

Status: deliberately deferred until the acceptance and readiness contracts are
stable enough to display without duplicating business rules.

The first graphical surface should remain read-only and consume deterministic
report projections. It should make corpus progress, external blockers, case and
charge status, expected/invoiced/paid comparisons, evidence gaps, and governing
source links visible to an audit professional. Framework selection, editing,
ingest, submission, and money movement are not implied by this seed.
