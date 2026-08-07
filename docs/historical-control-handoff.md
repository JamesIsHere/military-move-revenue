# Historical Control Handoff

- Policy ID: `HISTORICAL-CONTROL-HANDOFF-V1`
- Version: `2026-08-07.1`
- Effective period: 2026-08-07 until superseded
- Scope: Domestic DP3 TSP-to-Government read-only post-audit acceptance
- Authority: ratified `goal.md`, `HISTORICAL-INTAKE-CONTROL-V1`,
  `HISTORICAL-EXPECTED-LABEL-CONTROL-V1`, and
  `HISTORICAL-CORPUS-MANIFEST-V1`

This verifier treats the intake envelope, expected-label approval control, and
current manifest entry as one cross-control handoff. It validates every
component under its own policy, selects the single current manifest entry for
the opaque case, and then verifies all IDs, hashes, modes, timestamps, and
pre-execution boundaries across the three components.

## Cross-control contract

The intake, label control, and manifest must use the same control mode and case
reference. The evaluation time equals the manifest cutoff. The current manifest
entry must link the exact intake-envelope ID and canonical SHA-256, sanitized-
bundle SHA-256, expected-label ID and SHA-256, and must be registered no earlier
than label approval. A pre-execution handoff cannot carry an acceptance-report
link.

The result includes canonical hashes for all three inputs, the current immutable
manifest entry identity/version/status, corpus progress, ordered blockers,
provenance, and presentation-neutral display fields. Rebuilding the result is
the only validation method; caller-supplied readiness, authority, counts,
blockers, or display values are rejected.

## Synthetic result

The synthetic fixtures produce `SYNTHETIC_LINKS_VERIFIED_NON_OPERATIONAL`.
Linkage is verified, but operational readiness and acceptance-execution
authority remain false and the result never counts toward 25. Four blockers
remain explicit: synthetic intake is not authorization, synthetic label control
is not expert approval, the synthetic manifest is non-counting, and 25 passing
authorized historical cases are still required.

This distinction is deliberate: structurally correct links are not evidence of
real authorization.

## Operational states

No positive operational fixture exists. After separately authorized sanitized
controls become available, a current `REGISTERED_CONTROLS_VERIFIED` entry may
produce `CONTROLS_VERIFIED_PENDING_EXECUTION_RELEASE`. It remains blocked until
an explicit immutable manifest transition to `READY_FOR_ACCEPTANCE_EXECUTION`.
Only that current status can produce a ready pre-execution handoff.

Executed, failed, blocked, or report-linked entries are rejected by this
pre-execution verifier. Their evidence belongs to the later acceptance-result
and manifest-version path.

## Interface boundary

The title, headline, progress label, primary action, blocker count, linked-
control summary, and ordered blockers form a read model for the future operator
interface. The interface must display this deterministic result and must not
recalculate or override readiness.
