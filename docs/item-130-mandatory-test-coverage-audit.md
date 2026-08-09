# Item 130 Mandatory-Test Coverage Audit

Current audit ID: `ITEM-130-MANDATORY-COVERAGE-2026-08-07-3`

## Result

All 18 categories in the ratified Item 130 non-monetary synthetic contract are
covered. Both test gaps found by audit version 1 are closed. Item 130 financial
and mapping authority remains prohibited, and four source gaps plus `CF-0001`
and `CF-0003` remain open.

The current machine-checkable source record is
`docs/decisions/0005-item-130-mandatory-test-coverage-audit-3.json`. It
supersedes, but does not rewrite, immutable audit versions 1 and 2. The validator
checks both historical hashes, re-runs all seven fixture validators, verifies
the correction chain, and rejects six exact, camel-case, and nested forbidden-
output aliases.

## Coverage

| # | Mandatory category | Status | Primary evidence |
|---:|---|---|---|
| 1 | Direct positive candidates for 130A–130J | Covered | `SYNTH-LS-013`–`016`, `019` |
| 2 | Similar unlisted article does not auto-classify | Covered | `SYNTH-LS-019` upright-piano exclusion |
| 3 | Motorcycle 249/250-cc boundary | Covered | `SYNTH-LS-013` plus 249-cc mutation |
| 4 | Television 48-inch and flat-screen boundary | Covered | `SYNTH-LS-014` |
| 5 | 130I/130J volume and assembled state | Covered | `SYNTH-LS-015` |
| 6 | Boat 14-foot, fraction, and measurement methods | Covered | `SYNTH-LS-016` |
| 7 | Boat width/height, HHG co-move, and OTO context | Covered | `SYNTH-LS-016` |
| 8 | Associated trailer present/absent/unknown | Covered | `SYNTH-LS-016` |
| 9 | Government-preapproval blocked states | Covered | `SYNTH-LS-017` |
| 10 | Code 2 and crating exclusions remain distinct | Covered | `SYNTH-LS-017` |
| 11 | Hand-carry/carton exclusion and named exceptions | Covered | `SYNTH-LS-017` |
| 12 | Shuttle-transload exclusion | Covered | `SYNTH-LS-017` |
| 13 | Loading/unloading pairing cardinalities | Covered | `SYNTH-LS-018` |
| 14 | SIT pairing and three cause states | Covered | `SYNTH-LS-018` |
| 15 | Lawnmower and 130E listing gaps | Covered | Decision 0005 dossier validator and `SYNTH-LS-016` |
| 16 | 130F BOTO scope gap | Covered | Decision 0005 dossier validator and `SYNTH-LS-016` |
| 17 | Decimals, units, evidence, and immutable corrections | Covered | `SYNTH-LS-013` 249-cc-to-250-cc direct correction chain |
| 18 | No financial or mapping output | Covered | Shared recursive guard plus six alias/nesting probes |

## Boundary after completion

This completes only the ratified public-source non-monetary synthetic Item 130
test contract. It does not authorize a billing mapping, rate-date fact, billable
quantity, rate, amount, rule package, audit adapter, or historical-case
acceptance. Further Item 130 financial work requires authoritative closure and a
separate approved decision.
