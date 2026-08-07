# Historical Corpus Manifest and No-Data Onboarding Runbook

- Policy ID: `HISTORICAL-CORPUS-MANIFEST-V1`
- Version: `2026-08-07.1`
- Effective period: 2026-08-07 until superseded
- Scope: Domestic DP3 TSP-to-Government read-only post-audit acceptance corpus
- Authority: ratified `goal.md` completion verifier and sensitive-data boundary

This contract provides a safe landing zone for a future authorized historical
corpus. The checked-in manifest is empty, contains no case content, authorizes no
ingest, and deterministically evaluates to zero passing cases with 25 remaining.

## Manifest contract

The manifest stores control metadata only. A future entry links an opaque case
reference to an operational intake-envelope ID and SHA-256, sanitized-bundle
SHA-256, independently approved expected-label ID and SHA-256, immutable entry
version, direct supersession reference, status, scope, registration time, and
provenance. Executed statuses also require the deterministic acceptance-report
ID and SHA-256; unexecuted and synthetic entries cannot carry that link.
Shipment records, names, addresses, identifiers, signatures,
accounts, and source-document metadata are prohibited.

Input carries only the declared number of registered entry versions. Passing,
failed, blocked, pending, current-case, remaining-case, and completion counts are
always derived. A caller cannot declare a passing count.

Entry IDs and case-version pairs are unique. Intake, sanitized-bundle, and label
hashes may repeat only across versions of the same opaque case. Versions must be
contiguous, registration times cannot move backward, and each version after one
must directly supersede its predecessor. Only the current version of each case
contributes to derived status counts.

## Modes

`EMPTY_AWAITING_AUTHORIZATION` is the checked-in zero-entry state. It sets
real-data ingest authority false and cannot contain entries.

`SYNTHETIC_TEMPLATE` exists only to test entry linkage, uniqueness,
supersession, and non-counting behavior. All IDs are visibly synthetic, no case
content is present, and the operational evaluator rejects the mode.

`OPERATIONAL` is reserved for separately authorized, sanitized historical
metadata. No positive operational manifest or entry exists until written
authorization and an approved sanitization process are available.

## No-data onboarding runbook

1. The authorized data owner supplies written authorization covering domestic
   DP3 TSP-to-Government post-audit and names the authorized control roles.
2. Sanitization occurs outside the development environment using an approved,
   versioned method. The raw source never enters this workspace.
3. An independent reviewer verifies prohibited-data and hidden-metadata removal
   and records the sanitized-bundle SHA-256.
4. Authorization, sanitization, ingest, retention, and outcome-review metadata
   are recorded in an operational `HISTORICAL-INTAKE-CONTROL-V1` envelope.
5. The expected outcome is independently expert-approved before execution and
   stored separately from deterministic financial inputs. Its metadata-only
   approval envelope passes `HISTORICAL-EXPECTED-LABEL-CONTROL-V1` and links to
   the validated intake envelope and sanitized-bundle hash.
6. A manifest entry is registered using opaque IDs and hashes only. Entry
   metadata is validated before any acceptance execution. The intake envelope,
   expected-label control, and current manifest entry then pass
   `HISTORICAL-CONTROL-HANDOFF-V1` as one linked pre-execution chain.
7. Corrections create a new manifest entry version that directly supersedes the
   prior version; prior versions are never rewritten.
8. The acceptance report runs only after envelope, manifest, scope, label, and
   bundle-link checks pass. Its ID and hash are registered in a new immutable
   entry version. Counts are derived from current executed results with report
   links.

## Handoff checklist

- Written authorization reference, validity period, scope, owner, and verifier
- Approved sanitization method ID/version and independent review evidence
- Sanitized-bundle SHA-256, with no raw-source artifact in the workspace
- Operational intake-envelope ID and SHA-256
- Retention classification, approval, and deletion date
- Independent expected-label ID, SHA-256, reviewer role, and approval time
- Expected-label approval-control envelope ID and policy version
- Deterministic acceptance-report ID and SHA-256 after execution
- Opaque case reference and immutable manifest entry version
- Confirmed domestic DP3 TSP-to-Government completed-shipment scope
- Explicit confirmation that the manifest and envelope contain no case content
- Deterministic control-handoff result with verified linkage and no blockers

Until every item is available and independently verified, the corpus remains
empty and historical acceptance remains zero of 25.

The deterministic no-data view of those missing requirements is governed by
`HISTORICAL-CORPUS-NO-DATA-PREFLIGHT-V1` in
`docs/historical-corpus-preflight.md`. That report is diagnostic only and does
not replace any onboarding evidence.
