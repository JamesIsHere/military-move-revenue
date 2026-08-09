# Decision 0006 — CF-0004 Initial-Net Scoped Interpretation

- Status: Accepted
- Date: 2026-08-07
- Approver: Project owner, by explicit session approval of Alternative A
- Scope: Domestic 400NG Items 4.5 and 4.13 for the 2026 rate cycle only
- Proposal preserved at: `0006-cf-0004-reweigh-tolerance-dossier.md` and
  `0006-cf-0004-reweigh-tolerance-dossier.json`

## Decision

The project owner selected `A_APPROVE_INITIAL_NET_SCOPED`. For actual pickup
dates from 2026-05-15 through 2027-05-14, the final reviewed initial net scale
weight selects the 5,000-pound branch in:

- Item 4.5 lower-reweigh fee tolerance; and
- Item 4.13 completed containerized-reweigh reimbursement tolerance.

Exactly 5,000 pounds uses the “5,000 pounds or less” branch. No selector may be
inferred when the initial net result is missing, blocked, conflicting,
unreviewed, constructive-only, or otherwise invalid.

The approved formulas are:

```text
branch := AT_OR_BELOW_5000 when initial_net_lb <= 5000, otherwise OVER_5000

lower-reweigh fee:
  reweigh_net_lb >= initial_net_lb
  OR branch = AT_OR_BELOW_5000 AND difference_lb < 150
  OR branch = OVER_5000 AND difference_lb < lower_net_lb * 0.05

containerized reimbursement:
  reweigh_tare_lb > original_tare_lb
  AND (
    branch = AT_OR_BELOW_5000 AND tare_increase_lb > 150
    OR branch = OVER_5000 AND tare_increase_lb >= lower_tare_lb * 0.05
  )
```

All weight arithmetic is exact decimal pounds with no invented rounding.

## Rationale and authority boundary

The tariff does not expressly identify the branch fact. Initial net is approved
as the narrow interpretation because it exists before both decisions, is an
explicit Item 4.5 operand, is stable across later observations, and avoids
making branch selection depend on the result being tested. Advisory 23-0004's
lesser-weight direction occurs after tolerance qualification and therefore does
not override this selector.

This is registered as `INT-0003`. It resolves `CF-0004` only for the stated
2026 scope. Reopen the conflict for a later rate cycle or when an applicable
amendment, advisory, written publisher clarification, worked example, or
contrary adjudicative authority is archived.

## Exclusions

This decision does not authorize:

- a reweigh-fee rate, Item 226A or another billing-code contract, or discount
  treatment;
- reimbursement, refund, or charge-allocation amounts;
- constructive-only substitution for a missing reviewed initial net;
- dates after 2027-05-14;
- live invoice submission, external communication, or money movement; or
- resolution of `CF-0001` or `CF-0003`.

## Publication gate

Publication requires the thirteen mandatory dossier tests, effective-period
gates, reviewed input evidence, upstream-block propagation, exact `Decimal`
arithmetic, result provenance, and tamper rejection. Outputs are eligibility
decisions only and must not contain monetary amounts.

