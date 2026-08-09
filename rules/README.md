# Rules

The first executable reference family is implemented in
`weight_determination.py`. It calculates an initial net scale weight using exact
decimal arithmetic and blocks the result when required scale, weighing-condition,
or ticket evidence facts are not established.

`automatic_reweigh.py` implements the separate Item 4.8 requirement decision.
It consumes a final initial-weight result and an explicitly supplied grade band;
it does not infer a person's grade, calculate a fee, or select the controlling
weight after reweigh.

`completed_reweigh_selection.py` selects the lowest net from current completed
reweigh-observation versions using exact decimal comparison. Every current
observation must have reviewed determining-ticket evidence and a complete DPS
update. The selector preserves ties and does not compare the result with the
initial weight or apply fee, tolerance, refund, billing, or monetary logic.

`scale_reweigh_lower_reference.py` consumes only verified results from the
initial-weight and completed-reweigh packages and returns their exact lower
scale-weight reference. It propagates upstream blockers, preserves equal-weight
ties, and does not decide charge-specific weight use or produce billing logic.

`constructive_weight_reference.py` calculates exact verified cubic volume times
7 lb per cubic foot and selects the lower valid-ticket or constructive reference.
It requires reviewed volume evidence, responsible-PPSO approval, and either a
verified upstream ticket result or documented lost-ticket status. No source
rounding rule is invented.

`containerized_provisional_weight.py` implements only 400NG Item 4.13(1)-(2).
It subtracts the reviewed original tare from the reviewed new gross using exact
decimal arithmetic, then selects the lower final initial or provisional net.
Later new-tare reimbursement tolerance remains outside the package.

`reweigh_tolerance.py` implements Decision 0006 / `INT-0003` for 2026 Items 4.5
and 4.13. Final reviewed initial net selects the 5,000-pound branch. The module
returns exact-decimal fee-qualification and reimbursement-tolerance booleans,
propagates upstream/evidence blockers, and emits no rate, billing code, amount,
invoice, refund allocation, or money result.

`reweigh_refund_workflow.py` consumes a provenance-complete lower scale-weight
result and immutable workflow facts. It decides whether the post-invoice path
requires a supplemental refund and whether the destination/direct-delivery hold
is ready to release. It emits no refund amount, fee, tolerance, billing code, or
payment result.

`item_28a_extra_pickup.py` is the first monetary shadow-rating family. It uses
the original requested pickup date to select the immutable 2026 package, counts
only reviewed, completed, Origin-PPSO-authorized extra pickups after the first,
applies the self-storage-only exclusion, and multiplies the exact occurrence
count by `Decimal("198.50")`. Blocked evidence produces no amount or line action.
The package is limited by Decision 0003 / `INT-0001` and cannot be generalized
to Item 28B, Item 28C, or another item-code row.

`item_28a_post_audit.py` consumes only a provenance-complete result from that
published package plus immutable, reviewed invoice/payment history. It selects
current superseding versions, requires reviewed completeness through the audit
cutoff, matches only the accepted raw `28A`/`EA` contract, and computes exact
invoiced-minus-expected, paid-minus-invoiced, and paid-minus-expected variances.
Ambiguous matching, incomplete history, missing evidence, or blocked upstream
rating produces no authoritative comparison and enters human review. Its
versioned internal policy is documented in
`docs/item-28a-post-audit-policy.md`; it is not a new Government billing rule.

`item_28b_extra_delivery.py` implements the separately approved `INT-0002`
contract using actual pickup date, completed extra deliveries before final
delivery, Destination-PPSO authorization, reviewed evidence, and exact
occurrence multiplication. `item_28b_post_audit.py` applies the shared internal
occurrence-reconciliation core under its own Item 28B policy, package,
provenance, mapping decision, and adapter contract.

`audit_report.py` registers distinct Item 28A and Item 28B adapters. A single
shipment report may contain both families; any blocked family suppresses all
aggregate monetary totals without suppressing decided charge-level findings.

`historical_acceptance.py` executes source-structured rating facts through the
registered audit-report adapters, compares the deterministic projection with a
separately authored expected-outcome label, and aggregates corpus readiness.
Each adapter may receive a provenance-complete charge-scoped audit record view;
otherwise it consumes the case's shared audit records.
Synthetic benchmarks and public precedents remain visible but cannot increment
the ratified 25-case counter. Only written-authorized, pre-ingest-sanitized,
independently expert-labeled historical cases are eligible.

`historical_intake.py` validates the separate metadata-only control envelope
required by that historical tier. It enforces current written-authorization
metadata, sanitization-before-ingest chronology, bundle hashing, prohibited-data
removal, retention, distinct critical roles, provenance, and the no-AI-
attestation boundary. Its synthetic template is structurally testable but can
never authorize operational ingest.

`historical_corpus_manifest.py` validates the metadata-only registry that will
link future authorized cases to those intake envelopes, sanitized-bundle
hashes, and independently approved expected-label hashes. The checked-in
manifest is an immutable empty state at zero of 25. Counts are derived from
current directly superseding entry versions; synthetic templates exercise the
contract but cannot produce a pass or authorize operational use.

`historical_corpus_preflight.py` converts that checked-in empty state into a
deterministic, presentation-neutral readiness report. It exposes zero-of-25
progress, eight provenance-linked external blockers, and one next action. The
report is non-authorizing, contains no case content, rejects non-empty and
synthetic manifest modes, and is suitable as a future graphical interface's
read model without moving control logic into the interface.

`historical_expected_label.py` validates the metadata-only approval envelope
for a separately stored expected-outcome label. It binds the label ID/hash to a
validated intake envelope, bundle hash, opaque case reference, pre-execution
chronology, independent author and expert reviewer roles, provenance, and no-AI
attestation. The synthetic template contains neither an outcome nor label
artifact and cannot authorize operational use.

`historical_control_handoff.py` rebuilds a single cross-control readiness result
from the intake envelope, expected-label control, and current manifest entry. It
verifies all case, control, bundle, label, entry, hash, and timestamp links and
keeps structural linkage separate from operational authority. Its synthetic
result verifies the links but remains blocked, non-counting, and unable to
authorize acceptance execution.

The file-backed physical source/rule registry is under `rules/registry/`. Its
seven reference/workflow packages and two monetary packages are published
separately from the draft, non-executable rules affected by open conflicts.

Every future executable rule must identify its source version and locator,
effective period, required facts, calculation or decision, evidence requirements,
precedence, and regression cases.
