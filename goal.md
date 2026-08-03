# Goal — Domestic DP3 Post-Audit v1

> Status: **RATIFIED — 2026-08-03**

## Outcome

A moving company can provide the records for a completed domestic DP3 shipment,
and the system can reconstruct what the TSP should have billed the government,
identify missing, unsupported, underbilled, overbilled, or incorrectly paid
charges, and explain every conclusion using the governing source and supporting
evidence.

## First user

A moving-company billing or audit professional reviewing completed domestic DP3
shipments for a TSP.

## Baseline

The project begins with public regulations, tariffs, rate and reference data,
forms, interface specifications, advisories, and public decisions. An authorized
sanitized historical corpus is not yet available and will be acquired separately.

## Version-one boundary

Included:

- Domestic DP3 shipments governed by 400NG.
- TSP-to-government charges.
- Read-only post-audit of completed shipments.
- Expected, invoiced, and paid amount comparison.
- Charge-level evidence and source explanations.
- Effective-dated rule and rate versions.
- Human review of ambiguity.

Excluded:

- Live invoice creation or submission to DPS/TPPS.
- Movement of money or collection activity.
- Agent-to-TSP compensation schedules.
- International Tender shipments.
- Non-Temporary Storage as a separate program.
- Direct Procurement Method billing.
- Claims adjudication.
- GSA civilian and commercial relocation billing.

## Quality bar

- No billing rule exists without authoritative provenance.
- No monetary amount relies on binary floating-point arithmetic.
- No ambiguity is silently converted into a definitive result.
- Historical rule versions remain reproducible.
- Every calculated invoice line is explainable from facts, rules, rates, and
  evidence.
- Sensitive or proprietary data is not used without authorization.

## Decision defaults

- Prefer the narrowest interpretation supported by authoritative text; flag
  competing interpretations for review.
- Prefer normalized records for stable domain concepts and versioned reference
  tables for controlled values.
- Preserve original external identifiers and payloads at integration boundaries,
  but do not make the internal domain model mirror one external system.
- Model events and repeated observations—such as weights, submissions, and
  statuses—as child records rather than overwriting a latest-value column.
- Use public sources to draft the schema; use real authorized cases to validate
  optionality, cardinality, and correctness.

## Allowed without asking

- Read and archive publicly available authoritative documents.
- Create source inventories, structured extracts, schemas, diagrams, synthetic
  fixtures, and deterministic tests.
- Revise `plan.md`, `state.md`, and derived design documents within this goal.
- Record open questions and conservative assumptions.

## Approval required

- Ingesting any real shipment or employer data.
- Accessing authenticated government or vendor systems.
- Submitting invoices, sending messages, or changing external records.
- Expanding to another billing relationship or program.
- Changing the outcome, completion test, or sensitive-data boundary.

## Forbidden

- Scraping authenticated Daycos, DPS, TPPS, or other third-party systems without
  authorization.
- Copying proprietary software, customer data, or private rule interpretations.
- Using unsanitized real personal data in development or tests.
- Treating probabilistic AI output as the authoritative financial result.

## Completion verifier

Using at least 25 authorized, anonymized historical domestic military-move files
with expert-approved outcomes, the system:

1. Reconstructs every supported expected invoice line.
2. Identifies expected-versus-invoiced-versus-paid discrepancies.
3. Cites the governing source for each material decision.
4. Identifies the evidence supporting each charge.
5. Flags missing or ambiguous information instead of silently resolving it.

Until the historical corpus is available, synthetic boundary fixtures provide an
interim verifier but cannot complete the goal.

## Completion proof

Completion requires, at minimum:

- A versioned source registry and archived authoritative source set.
- A documented canonical shipment and billing schema.
- Deterministic rule and rating execution.
- Source-backed explanations.
- Synthetic boundary tests.
- A 25-case authorized historical acceptance report.
- A security and sanitization review for the data actually processed.
- `result.md` containing commands, outputs, limitations, and completion evidence.

## Iteration and recovery

Difficulty, uncertainty, and failed first attempts are not blockers. Record the
failure, preserve useful evidence, revise the plan, and continue. A blocker must
identify the missing authority or evidence, attempted alternatives, and the exact
decision or access needed from the user.
