# Historical Expected-Label Approval Control

- Policy ID: `HISTORICAL-EXPECTED-LABEL-CONTROL-V1`
- Version: `2026-08-07.1`
- Effective period: 2026-08-07 until superseded
- Scope: Domestic DP3 TSP-to-Government read-only post-audit acceptance
- Authority: ratified `goal.md`, `HISTORICAL-INTAKE-CONTROL-V1`, and the
  historical acceptance independent-outcome requirement

This metadata-only envelope proves how a separately stored expected-outcome
label was authored and approved before deterministic acceptance execution. It
contains the label's opaque ID and SHA-256, never the expected projection,
shipment facts, invoice facts, money, evidence documents, or other case content.

## Contract

The control links one opaque case reference to an exact intake-envelope ID and
canonical SHA-256, sanitized-bundle SHA-256, expected-label ID and SHA-256,
author role and time, expert reviewer role and time, execution boundary, and
provenance. The linked intake envelope is validated first.

Authorship must occur after the sanitized-bundle ingest checkpoint. Independent
expert approval must occur after authorship and no later than evaluation. The
author and reviewer are distinct; the author is also distinct from the intake
authorization verifier, sanitization reviewer, and ingest approver. The reviewer
must equal the outcome-reviewer role already reserved in the intake envelope,
which itself is distinct from those critical intake roles.

AI may help locate or summarize source material under the project AI boundary,
but it cannot author the authoritative expected outcome or attest its approval.
Both AI indicators are therefore false.

The control is registered before acceptance execution. Its execution status is
`NOT_STARTED`, it has no first-execution time, and it records that approval must
precede execution. A later acceptance report is linked through a new immutable
corpus-manifest entry version; this envelope is not rewritten.

## Modes

`SYNTHETIC_TEMPLATE` validates structure and cross-links only. Every identity is
visibly synthetic, the label hash is a placeholder with no stored artifact,
label-use authority is false, and the operational validator rejects it.

`OPERATIONAL` is reserved for a separately authorized sanitized case. It
requires a valid operational intake envelope, an externally stored sanitized
label artifact, expert approval, and label-use authority. No operational example
exists until written authorization and approved sanitization are available.

## Promotion boundary

Changing a synthetic status or mode never creates operational approval. A
future operational control must be built from real authorized control evidence,
validated against the actual intake envelope, and linked by exact hashes. This
contract does not authorize ingest and does not itself make a case count toward
the required 25.

`HISTORICAL-CONTROL-HANDOFF-V1` performs the reusable cross-check between this
envelope, the linked intake envelope, and the current corpus-manifest entry.
