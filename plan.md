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

Status: in progress. Item 28A now has the first end-to-end deterministic audit
slice: immutable corrected invoice/payment histories, reviewed completeness and
source-evidence gates, exact expected/invoiced/paid variances, decided finding
classifications, and human-review blocks. This does not yet cover another charge
family or authorized historical data.

Exit criteria:

- Evidence requirements attach to charge decisions.
- Expected, invoiced, and paid lines can be reconciled without loss of history.
- Missing, conflicting, and unsupported facts enter human-review queues.

## M6 — Historical acceptance

Exit criteria:

- At least 25 authorized sanitized cases are loaded through an approved process.
- Expert-approved outcomes are independently recorded.
- The completion verifier in `goal.md` passes or discrepancies are documented.
- Security, sanitization, and retention controls are reviewed.
