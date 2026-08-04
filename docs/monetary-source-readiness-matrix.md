# Monetary Charge Source-Readiness Matrix

- Assessment: `DP3-MONETARY-READINESS-2026-08-04-1`
- Gate policy: `MONETARY-SOURCE-READINESS-GATE-V1` / `2026-08-04.1`
- Scope: domestic DP3 TSP-to-Government post-audit
- Result: no second monetary family is source-ready

The authoritative structured assessment is
`docs/monetary-source-readiness-matrix.json`. `PASS` means archived reviewed
authority is sufficient for that dimension; `BLOCKED` means no money may be
published regardless of the other cells.

| Rank | Family | Rule | Rate/unit | Date selector | Item contract | Evidence | Audit match | Result |
|---:|---|---|---|---|---|---|---|---|
| Ref | Item 28A extra pickup | PASS | PASS | PASS (`INT-0001`) | PASS (`INT-0001`) | PASS | PASS | Ready, implemented |
| 1 | Item 28B extra delivery | PASS | PASS | BLOCKED (`CF-0001`, `CF-0003`) | BLOCKED (`CF-0003`) | BLOCKED (`CF-0003`) | PASS | Blocked |
| 2 | Item 4 reweigh fee | BLOCKED (`CF-0004`) | PASS | BLOCKED (`CF-0001`, `CF-0003`) | BLOCKED (`CF-0003`) | PASS | PASS | Blocked |
| 3 | Item 130 light/bulky | PASS | PASS | BLOCKED (`CF-0001`, `CF-0003`) | BLOCKED (`CF-0003`) | PASS | PASS | Blocked |
| 4 | Item 120 extra labor | PASS | PASS | BLOCKED (`CF-0001`, `CF-0003`) | BLOCKED (`CF-0003`) | PASS | PASS | Blocked |
| 5 | Item 105B crating | BLOCKED (volume rounding) | PASS | BLOCKED (`CF-0001`, `CF-0003`) | BLOCKED (`CF-0003`) | PASS | PASS | Blocked |
| 6 | Item 105A pack/unpack | BLOCKED (discount/order) | PASS | BLOCKED (`CF-0001`, `CF-0003`) | BLOCKED (`CF-0003`) | PASS | PASS | Blocked |

## Decision

Item 28B is the next decision candidate, not the next implemented rule. Current
400NG Item 28 directly defines additional deliveries, and the 2026 rate workbook
directly supplies 198.50 USD per occurrence. Its 2022 row 24 says actual-pickup
date, `28B`, `EA`, destination schedule/location, Destination PPSO, and approval
required. Those row fields remain outside `INT-0001`, and the actual-pickup date
conflicts with the incorporated workbook banner. Therefore no adapter or amount
is authorized yet.

The next bounded action is a Decision 0004 dossier that presents the competing
date claims, row-24 publication evidence, exact scope, exclusions, and mandatory
boundary tests. Owner approval is required before implementing Item 28B. If that
decision is not approved, the highest-leverage external acquisition remains a
current domestic item-code baseline/advisory chain; the reweigh fee additionally
needs authority identifying the 5,000-lb branch fact.
