# Item 28B Post-Audit Policy

- Policy ID: `AUDIT-DP3-ITEM-28B-RECONCILIATION-V1`
- Version: `2026-08-04.1`
- Status: Approved internal deterministic audit policy
- Effective period: 2026-08-04 until superseded
- Scope: Domestic DP3 Item 28B read-only TSP-to-Government post-audit
- Approval basis: Ratified `goal.md`, Decision 0004 / `INT-0002`, and the
  project owner's instruction to implement the second audit adapter

This policy governs comparison behavior. It does not create a Government billing
rule, alter immutable package `2026.item-28b-extra-delivery.1`, authorize another
item code, submit an invoice, or move money.

## Required inputs

An audit requires a provenance-complete Item 28B expected-charge result from
`RP-DP3-2026-ITEM-28B-1`; append-only invoice, line, payment, and allocation
history through the cutoff; reviewed source evidence for every observed version;
and separate reviewed `INVOICE_HISTORY` and `PAYMENT_HISTORY` completeness
assertions covering that cutoff.

A blocked expected charge blocks the audit. Missing or stale completeness cannot
be interpreted as a zero invoice or zero payment. The output preserves the
validated upstream result, shipment, evidence, and exact calculation trace.

## Current-version and matching policy

Corrections create contiguous immutable versions with direct `supersedes_id`
links. Only current invoice, line, and allocation versions participate in the
comparison; historical versions remain traceable.

A one-to-one match requires raw billed code `28B`, unit `EA`, mapping status
`ACCEPTED`, and interpretation decision `INT-0002`. Multiple current accepted
lines, a candidate-form code, or a mismatched interpretation enters human review
without an authoritative comparison.

## Exact calculations

All quantities and USD values are exact decimal strings. No binary floating
point or rounding is used.

- Billing variance: `invoiced_amount - expected_amount`
- Payment variance: `paid_amount - invoiced_amount`
- Realized variance: `paid_amount - expected_amount`
- Quantity variance: `invoiced_quantity - expected_quantity`

Payment is the sum of current reviewed allocations to the matched stable invoice
line. Every payment balances exactly to its current allocations.

## Findings and blocked results

The policy uses the same deterministic billing, quantity, payment, and overall
finding classifications as Item 28A. This is reuse of an internal comparison
policy, not reuse of Item 28A's Government billing interpretation.

Ambiguous matching, missing evidence, incomplete history, and blocked upstream
rating produce `AUDIT_BLOCKED`, require human review, and expose no comparison
amounts or variances. AI may extract candidate facts, but only reviewed facts
and deterministic code may produce the audit result.
