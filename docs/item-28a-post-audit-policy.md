# Item 28A Post-Audit Policy

- Policy ID: `AUDIT-DP3-ITEM-28A-RECONCILIATION-V1`
- Version: `2026-08-03.1`
- Status: Approved internal deterministic audit policy
- Effective period: 2026-08-03 until superseded
- Scope: Domestic DP3 Item 28A read-only TSP-to-Government post-audit
- Approval basis: Ratified `goal.md` and the project owner's instruction to
  execute the expected/invoiced/paid audit plan

This policy governs comparison behavior. It does not create a Government billing
rule, alter immutable package `2026.item-28a-extra-pickup.1`, authorize another
item code, submit an invoice, or move money.

## Required inputs

An audit requires:

1. a provenance-complete `FINAL` Item 28A expected-charge result from
   `RP-DP3-2026-ITEM-28A-1`;
2. append-only invoice, invoice-version, line, and line-version history through
   the audit cutoff;
3. append-only payment and allocation history through the audit cutoff;
4. reviewed source evidence for every observed invoice version, line version,
   payment, and allocation; and
5. separate reviewed `INVOICE_HISTORY` and `PAYMENT_HISTORY` completeness
   assertions covering the audit cutoff.

A blocked expected charge blocks the audit. Missing or stale completeness cannot
be interpreted as a zero invoice or zero payment.

## Current-version and matching policy

Corrections create contiguous immutable versions with direct `supersedes_id`
links. Only the current invoice, line, and allocation versions participate in
the comparison; historical versions remain in the input snapshot.

A one-to-one match requires raw billed code `28A`, unit `EA`, mapping status
`ACCEPTED`, and interpretation decision `INT-0001`. Multiple current accepted
lines, a candidate-form code, or a mismatched interpretation enters human review
without an authoritative comparison.

## Exact calculations

All values are exact decimal strings in USD. No binary floating point or
rounding is used.

- Billing variance: `invoiced_amount - expected_amount`
- Payment variance: `paid_amount - invoiced_amount`
- Realized variance: `paid_amount - expected_amount`
- Quantity variance: `invoiced_quantity - expected_quantity`

Payment is the sum of current reviewed allocations to the matched stable invoice
line. Every payment must balance exactly to its current allocations.

## Finding classifications

Billing findings are:

- `CORRECTLY_BILLED` when expected and invoiced amounts are equal;
- `MISSING_EXPECTED_CHARGE` when a positive expected charge has no matched line;
- `UNSUPPORTED_BILLED_CHARGE` when a matched line exists but expected amount is
  zero;
- `UNDERBILLED` when invoiced amount is below expected amount;
- `OVERBILLED` when invoiced amount is above expected amount; and
- `NO_CHARGE_EXPECTED_OR_BILLED` when both are affirmatively zero/absent.

Quantity is independently `QUANTITY_MATCH` or `QUANTITY_MISMATCH`. Payment is
independently `PAID_AS_INVOICED`, `UNPAID`, `PARTIALLY_PAID`, `OVERPAID`, or
`NO_MATCHED_INVOICE_LINE`.

A finding is `CLOSED_NO_EXCEPTION` only when billing and quantity agree and the
matched line is paid as invoiced, or when complete history proves no charge was
expected or billed. Every other decided finding is `OPEN`.

## Blocked results and AI boundary

Ambiguous matching, missing evidence, incomplete history, and blocked upstream
rating produce `AUDIT_BLOCKED`, require human review, and expose no comparison
amounts or variances. AI may help extract candidate invoice/payment facts, but
only reviewed facts and deterministic code may produce the audit result.
