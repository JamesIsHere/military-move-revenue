# Plan

## M0 — Ratify the product contract

Status: complete on 2026-08-03.

Exit criteria:

- `goal.md` has been red-penned and explicitly ratified.
- The first user, financial relationship, program, completion verifier, and
  exclusions are unambiguous.

## M1 — Establish the source foundation

Exit criteria:

- Mandatory public sources are downloaded and checksummed.
- Every source has authority, scope, version, effective dates, supersession,
  retrieval, and extraction status.
- Governing and contextual sources are clearly separated.
- Source precedence and conflict-handling policy are documented.

## M2 — Derive the canonical schema

Exit criteria:

- A source-to-field matrix covers shipment, party, location, weight, service,
  evidence, invoice, payment, rule, rate, and workflow concepts.
- Each field has a logical type, unit, cardinality, nullability rationale,
  sensitivity classification, validation, and provenance.
- Conceptual and logical ER diagrams exist.
- Unresolved domain questions are explicit.
- The schema is tested with synthetic straight-through and boundary cases.

## M3 — Implement the source and rule registry

Exit criteria:

- Source artifacts and versions can be registered immutably.
- Rules and rates reference precise source locations and effective periods.
- Supersession is explicit and historical versions remain reproducible.
- Automated validation rejects incomplete provenance.

## M4 — Implement shadow rating

Exit criteria:

- Structured shipment facts can be entered without document extraction.
- A prioritized subset of domestic 400NG charges is calculated deterministically.
- Every result reports inputs, math, source, and evidence expectations.
- Synthetic boundary tests pass.

## M5 — Add evidence and post-audit comparison

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
