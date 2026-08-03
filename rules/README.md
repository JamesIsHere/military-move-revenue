# Rules

The first executable reference family is implemented in
`weight_determination.py`. It calculates an initial net scale weight using exact
decimal arithmetic and blocks the result when required scale, weighing-condition,
or ticket evidence facts are not established.

`automatic_reweigh.py` implements the separate Item 4.8 requirement decision.
It consumes a final initial-weight result and an explicitly supplied grade band;
it does not infer a person's grade, calculate a fee, or select the controlling
weight after reweigh.

The file-backed physical source/rule registry is under `rules/registry/`. Its
Item 4 weight package is published separately from the draft, non-executable
rules affected by open conflicts.

Every future executable rule must identify its source version and locator,
effective period, required facts, calculation or decision, evidence requirements,
precedence, and regression cases.
