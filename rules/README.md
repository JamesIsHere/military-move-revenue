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

`reweigh_refund_workflow.py` consumes a provenance-complete lower scale-weight
result and immutable workflow facts. It decides whether the post-invoice path
requires a supplemental refund and whether the destination/direct-delivery hold
is ready to release. It emits no refund amount, fee, tolerance, billing code, or
payment result.

The file-backed physical source/rule registry is under `rules/registry/`. Its
seven reference/workflow packages are published separately from the draft,
non-executable rules affected by open conflicts.

Every future executable rule must identify its source version and locator,
effective period, required facts, calculation or decision, evidence requirements,
precedence, and regression cases.
