# Decision 0001 — Version-One Scope

- Status: Accepted in planning conversation; incorporated into draft goal
- Date: 2026-08-03

## Context

Daycos-like revenue operations span government billing, private agent
compensation, multiple personal-property programs, document workflows, invoice
submission, payment reconciliation, and recovery. Attempting all relationships
and programs would prevent a source-grounded initial schema and verifier.

## Decision

Version one is a read-only post-audit system for domestic DP3 shipments. It
reconstructs the amount a TSP should bill the government under the applicable
400NG rule and rate package. It does not submit invoices or calculate private
agent compensation.

## Consequences

- Public authoritative sources can support provisional schema and rule work.
- A historical authorized corpus is still required for completion.
- International, NTS, DPM, claims, private compensation, and live submission are
  deferred.
- The internal model should allow future financial relationships without making
  them part of current implementation or verification.

