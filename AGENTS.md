# Agent Operating Policy

## Required session loop

1. Read `goal.md`, `state.md`, and the active milestone in `plan.md`.
2. Select one verifiable outcome.
3. Make the smallest coherent change that advances that outcome.
4. Verify the change against source material or fixtures.
5. Append a concise entry to `worklog.md`.
6. Rewrite `state.md` as an honest cold-resume snapshot.

## Source discipline

- Every field, controlled value, calculation rule, evidence requirement, and
  workflow transition must identify its provenance.
- Provenance should include source ID, document version, effective period,
  section/item/page when available, retrieval date, and interpretation status.
- Preserve raw source files unchanged. Derived text and structured extracts must
  link back to the raw source and record how they were produced.
- Do not treat search snippets as the permanent source record. Obtain and archive
  the authoritative artifact before marking extraction complete.
- When sources conflict, record both claims and escalate the interpretation.

## Rules and calculations

- Use exact decimal arithmetic for money and explicit units for quantities.
- Rule packages and rate tables are immutable after publication in the system.
- Corrections create new versions; they do not rewrite historical versions.
- Select rules using the legally relevant effective-date fact.
- Each result must expose its inputs, rule version, calculation, evidence, and
  unresolved assumptions.
- Add boundary and regression tests for every implemented rule.

## AI boundary

AI may classify documents, extract candidate facts, locate relevant passages,
and draft explanations. Deterministic code and approved rule packages must
produce financial calculations. Low-confidence or conflicting facts require
human review.

## Sensitive data

- Do not ingest real shipment files without written authorization.
- Sanitization must occur before files enter the development environment.
- Do not store names, addresses, signatures, personal identifiers, financial
  account data, live government identifiers, or hidden document metadata in
  fixtures.
- Synthetic and sanitized fixtures must be labeled distinctly.

## Scope control

Version one is domestic DP3 TSP-to-government post-audit. International, NTS,
DPM, claims adjudication, private agent compensation, and live invoice submission
are out of scope unless `goal.md` is deliberately amended and re-ratified.

