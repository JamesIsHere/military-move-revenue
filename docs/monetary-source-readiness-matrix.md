# Monetary Charge Source-Readiness Matrix

- Assessment: `DP3-MONETARY-READINESS-2026-08-07-3`
- Gate policy: `MONETARY-SOURCE-READINESS-GATE-V1` / `2026-08-07.2`
- Scope: domestic DP3 TSP-to-Government post-audit
- Result: Items 28A and 28B are implemented; no third monetary family is
  source-ready

The authoritative structured assessment is
`docs/monetary-source-readiness-matrix.json`. `PASS` means archived reviewed
authority is sufficient for that dimension; `BLOCKED` means no money may be
published regardless of the other cells.

| Rank | Family | Rule | Rate/unit | Date selector | Item contract | Evidence | Audit match | Result |
|---:|---|---|---|---|---|---|---|---|
| Ref | Item 28A extra pickup | PASS | PASS | PASS (`INT-0001`) | PASS (`INT-0001`) | PASS | PASS | Ready, implemented |
| Ref | Item 28B extra delivery | PASS | PASS | PASS (`INT-0002`) | PASS (`INT-0002`) | PASS | PASS | Ready, implemented |
| 1 | Item 4 reweigh fee | PASS (`INT-0003`) | PASS | BLOCKED (`CF-0001`, `CF-0003`) | BLOCKED (`CF-0003`) | PASS | PASS | Blocked |
| 2 | Item 130 light/bulky | PASS | PASS | BLOCKED (`CF-0001`, `CF-0003`) | BLOCKED (`CF-0003`) | PASS | PASS | Blocked |
| 3 | Item 120 extra labor | PASS | PASS | BLOCKED (`CF-0001`, `CF-0003`) | BLOCKED (`CF-0003`) | PASS | PASS | Blocked |
| 4 | Item 105B crating | BLOCKED (volume rounding) | PASS | BLOCKED (`CF-0001`, `CF-0003`) | BLOCKED (`CF-0003`) | PASS | PASS | Blocked |
| 5 | Item 105A pack/unpack | BLOCKED (discount/order) | PASS | BLOCKED (`CF-0001`, `CF-0003`) | BLOCKED (`CF-0003`) | PASS | PASS | Blocked |

## Decision

Decision 0004 / `INT-0002` now supplies the narrow Item 28B date, code, unit,
location, and approval contract for the 2026 cycle. Its rating package and audit
adapter are published and verified. `CF-0001` and `CF-0003` remain open outside
that exact scope; Item 28B does not resolve any other candidate's gates.

Decision 0006 / `INT-0003` now supplies the 2026 initial-net tolerance selector,
and the two eligibility rules are published without money. The reweigh fee
remains the rank-one blocked monetary family because `CF-0001` and `CF-0003`
still block its scoped rate-date and billing-item contract. The project owner
deliberately deferred that deeper monetary fix as `DF-0001` on 2026-08-07
because the required authority is not available. The allowed result remains
`fee qualifies` or `fee does not qualify`; no current Item 226A, 4A/4B, note,
discount, rate-version, or dollar behavior may be inferred. The candidate keeps
rank one for eventual monetary work but is not the next active local task.
