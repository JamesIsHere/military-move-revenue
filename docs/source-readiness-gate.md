# Monetary Charge Source-Readiness Gate

- Gate ID: `MONETARY-SOURCE-READINESS-GATE-V1`
- Version: `2026-08-04.1`
- Status: Approved internal assessment policy
- Effective period: 2026-08-04 until superseded
- Scope: domestic DP3 TSP-to-Government post-audit monetary families
- Basis: ratified `goal.md`, Decision 0002 source precedence, and the project
  owner's instruction to build the source-readiness matrix

A family is `READY` only when all six gates are `PASS`:

1. governing eligibility and calculation rule;
2. numeric rate and explicit unit;
3. legally relevant effective-date selector;
4. current billing-item and controlled-field contract;
5. evidence requirement sufficient to decide eligibility; and
6. line-level invoice/payment audit matching support.

There is no weighted score. A high-value family with one material source gap is
still `BLOCKED`. Every pass cites reviewed archived provenance. Every block cites
the evidence already available, an open conflict or explicit internal gap, and
the exact artifact or decision required for closure. Candidate online text and
search snippets cannot satisfy a gate.

Ranking among blocked families is implementation sequencing, not authority. It
prefers the smallest fact/evidence expansion, reuse of published rules and audit
infrastructure, and value to the first user. Ranking never changes `BLOCKED` to
`READY` and never authorizes a financial calculation.

The machine-readable assessment is
`docs/monetary-source-readiness-matrix.json`. Corrections publish a new gate or
matrix version; historical versions remain in Git. AI may help draft or inspect
the matrix, but deterministic validation enforces its references and readiness
logic.
