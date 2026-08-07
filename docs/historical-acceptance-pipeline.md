# Historical Acceptance Pipeline Policy

- Policy ID: `HISTORICAL-ACCEPTANCE-PIPELINE-V1`
- Version: `2026-08-07.3`
- Effective period: 2026-08-07 until superseded
- Scope: Domestic DP3 TSP-to-Government read-only post-audit
- Authority: ratified `goal.md` completion verifier and sensitive-data boundary

This policy makes the acceptance harness operational before an authorized
historical corpus is available. It does not change the ratified completion
test, authorize real-data ingestion, approve a billing interpretation, or turn
synthetic or public examples into historical acceptance cases.

## Corpus tiers

`SOURCE_STRUCTURED_SYNTHETIC` cases exercise the same deterministic rating,
evidence, reconciliation, and reporting path intended for historical cases.
They must be explicitly synthetic, contain no real identifiers, and use an
independently authored synthetic expected-outcome label. A passing synthetic
case is a benchmark only and never counts toward the required 25.

`PUBLIC_PRECEDENT` records preserve an online decision candidate or an archived
authoritative decision as reference material. An unarchived candidate remains
URL-only and `PENDING_AUTHORITATIVE_ARCHIVE`; no claim extraction is marked
complete. An archived precedent requires repository-relative raw and derived
paths, separate SHA-256 values for both artifacts, and a documented extraction
method. Public precedents are reference-only, are not run as
current 400NG cases unless a separate in-scope executable bundle exists, and
never count toward the required 25.

`AUTHORIZED_SANITIZED_HISTORICAL` cases are the only acceptance-eligible tier.
Before execution, each case must carry verified written-authorization,
pre-ingest sanitization, and sensitive-data-review attestations. Its expected
outcome must be independently expert-approved before the corpus run. Passing
means that the deterministic report projection matches that fixed label; it
does not mean the case necessarily has no discrepancy or review block.
The metadata-only envelope and operational promotion rules are defined by
`HISTORICAL-INTAKE-CONTROL-V1`; a synthetic template is never an authorization.

## Executable case contract

An executable bundle supplies:

- provenance-backed scope facts establishing completed domestic DP3,
  TSP-to-Government, read-only post-audit use;
- provenance-backed authorization, sanitization, and sensitive-data controls;
- source-structured facts for each registered rating adapter;
- immutable invoice, payment, evidence, and completeness records shared by the
  charge audits;
- an audit cutoff; and
- a separately recorded expected-outcome projection.

Adapters normally consume the shared immutable audit record set. When an
adapter-specific evidence view is required, the charge input may carry a
provenance-complete record projection for that adapter. Synthetic fixture
assembly may derive such a view only through explicit, unique mutations beneath
the audit `records` object. This mechanism does not authorize mutation or
fabrication of historical records; authorized historical bundles must preserve
the actual sanitized source observations supplied to each adapter.

The pipeline executes each registered rating package, passes its verified
result into the matching post-audit adapter, and builds the canonical audit
report. The expected label is not accepted as a financial input. It is compared
only after deterministic execution.

The comparison includes report/review status, exact aggregate amounts and
variances, and each supported charge's expected, invoiced, and paid amounts,
quantities, and finding codes. Exact decimal strings remain unchanged; binary
floating-point inputs are rejected.

## Sensitive-data and provenance gate

Real shipment material may not enter the development environment before
written authorization and sanitization. Case bundles are recursively rejected
when they contain fields for names, street addresses, signatures, personal or
live Government identifiers, financial accounts, contact details, dates of
birth, or hidden document metadata. Passing this field-name guard supplements;
it does not replace, the required human sanitization review.

Scope, intake, expected-outcome, and public-precedent records require source ID,
document version, effective period, locator, retrieval date, and interpretation
status. Raw public sources remain unchanged. Derived public extracts must link
to the raw artifact and its checksum.

## Completion gate

The corpus report always separates synthetic benchmarks, public precedents,
and authorized historical cases. Only an authorized, sanitized, independently
expert-labeled historical case whose expected projection matches the
deterministic report increments the required-case counter.

Completion status is `READY` only when at least 25 such historical cases pass
and no eligible historical case fails. Until then the pipeline may be
`OPERATIONAL`, but completion remains `NOT_READY` and the report states the
remaining passing-case count.

## AI boundary

AI may locate public precedents, prepare candidate extracts, and draft labels
for expert review. It may not create the authoritative expected outcome for a
historical case, attest authorization or sanitization, calculate financial
results, approve a case, or clear a mismatch. Those transitions require the
recorded human controls and registered deterministic code described above.
