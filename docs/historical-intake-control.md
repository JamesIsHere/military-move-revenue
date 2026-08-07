# Historical Intake Control Policy

- Policy ID: `HISTORICAL-INTAKE-CONTROL-V1`
- Version: `2026-08-07.1`
- Effective period: 2026-08-07 until superseded
- Scope: Domestic DP3 TSP-to-Government read-only post-audit acceptance corpus
- Authority: ratified `goal.md` approval and sensitive-data boundaries

This policy defines the metadata gate that must pass before an authorized,
sanitized historical case may execute. It does not grant authorization, approve
a sanitization method, attach a historical bundle, or permit real data to enter
the development environment.

## Envelope boundary

The envelope contains control metadata only. It carries no shipment, person,
employer, account, Government identifier, address, signature, or hidden source
metadata. Exact field sets prevent case content from being smuggled into the
control record.

Every envelope identifies its scope, opaque case reference, authorization,
sanitization review, ingest checkpoint, retention decision, approval-role
separation, and provenance. The sanitized bundle is bound by a lowercase
SHA-256 value; the bundle itself is outside the metadata-only fixture.

## Authorization gate

Operational use requires written authorization whose effective period includes
both verification and evaluation. The authorization must explicitly cover
domestic DP3 TSP-to-Government post-audit, carry a nonempty reference, and be
verified by a role distinct from the data owner. Self-attestation is prohibited.

## Sanitization-before-ingest gate

Authorization verification must precede sanitization completion. Independent
sanitization review must precede ingest approval and the recorded ingest
checkpoint. The raw source must never enter the development environment before
sanitization. Hidden metadata removal and all required prohibited-data
categories must be explicitly verified. Sanitizer and reviewer roles must be
distinct.

## Retention and approval separation

An approved `SANITIZED_HISTORICAL_ACCEPTANCE` retention classification must be
current at evaluation and approved before ingest approval. Authorization,
sanitization review, ingest approval, and expected-outcome review use distinct
critical roles. AI may not attest any control or approve the expected outcome.

## Synthetic template

`SYNTHETIC_TEMPLATE` envelopes exist only to test this contract. They are
labeled `SYNTHETIC_METADATA_ONLY`, contain no case content, use synthetic
example statuses, and set `real_data_ingest_authorized` to false. The operational
validator rejects them; a synthetic template is never an authorization.
Changing the mode or authority flag cannot promote a
template because operational status, provenance, chronology, and control values
must all independently pass.

## Operational promotion

Only `OPERATIONAL` envelopes may accompany
`AUTHORIZED_SANITIZED_HISTORICAL` cases. They require verified written
authorization, verified pre-ingest sanitization, approved sanitized-bundle
ingest, approved retention, a current control period, and an expected-outcome
reviewer matching the independently expert-approved case label. No operational
positive fixture exists until real written authorization and an approved
sanitization process are available.
