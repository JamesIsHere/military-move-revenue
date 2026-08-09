# Historical Corpus No-Data Preflight

- Policy ID: `HISTORICAL-CORPUS-NO-DATA-PREFLIGHT-V1`
- Version: `2026-08-07.1`
- Effective period: 2026-08-07 until superseded
- Scope: Domestic DP3 TSP-to-Government read-only post-audit acceptance
- Authority: ratified `goal.md` and `HISTORICAL-CORPUS-MANIFEST-V1`

The preflight converts the authoritative empty corpus manifest into a
deterministic readiness report. It is diagnostic only: it cannot authorize
ingest, carry case content, register a case, satisfy a control, or produce a
historical pass.

## Input and output contract

The only permitted input is a valid `EMPTY_AWAITING_AUTHORIZATION` manifest.
Operational and synthetic manifests are rejected because this report describes
the no-data state only. The manifest ID, cutoff, policy version, and canonical
SHA-256 are included in the result.

The result exposes exact progress, a stable blocker catalog, provenance, a
single next action, and a small display projection. All values are rebuilt from
the manifest and policy. A caller cannot override authorization, blocker status,
passing count, remaining count, completion status, or display text.

The display projection is intentionally presentation-neutral. A later graphical
operator interface may render its title, headline, progress, action, and blocker
list without duplicating readiness logic. This policy does not select a web
framework or authorize interface work that changes the underlying controls.

## Blocker catalog

1. `WRITTEN_AUTHORIZATION_REQUIRED` — onboarding step 1 and the authorization
   handoff checklist item.
2. `APPROVED_SANITIZATION_METHOD_REQUIRED` — onboarding step 2 and the
   sanitization-method checklist item.
3. `INDEPENDENT_SANITIZATION_REVIEW_REQUIRED` — onboarding step 3 and the
   sanitized-bundle hash checklist item.
4. `OPERATIONAL_INTAKE_ENVELOPE_REQUIRED` — onboarding step 4 and the intake-
   envelope checklist item.
5. `INDEPENDENT_EXPECTED_LABEL_REQUIRED` — onboarding step 5 and the expected-
   label checklist item. `HISTORICAL-EXPECTED-LABEL-CONTROL-V1` defines the
   metadata and independence checks; its synthetic template cannot satisfy this
   operational blocker.
6. `AUTHORIZED_SANITIZED_CASE_ENTRY_REQUIRED` — onboarding steps 6-7 and the
   immutable manifest contract.
7. `ACCEPTANCE_EXECUTION_REPORT_REQUIRED` — onboarding step 8 and the required
   acceptance-report ID/hash link.
8. `PASSING_HISTORICAL_CASE_DEFICIT` — the ratified `goal.md` completion
   verifier and completion proof.

The first seven blockers record missing external artifacts or workflow results.
The eighth derives the exact remaining passing-case count. In the checked-in
empty state it is 25.

## Transition boundary

This no-data preflight remains blocked by design. A future operational readiness
path must validate actual written authorization, sanitization evidence, role
separation, intake-envelope content, expected-label independence, manifest
links, and acceptance-report hashes. It must be separately implemented and
tested after authorization exists; changing this report to `READY` is never a
valid transition.
