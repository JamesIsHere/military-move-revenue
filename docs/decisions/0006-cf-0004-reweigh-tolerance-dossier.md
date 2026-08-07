# Decision 0006 Dossier — CF-0004 Reweigh-Tolerance Branch Fact

- Status: **Proposed — explicit project-owner or counsel approval required**
- Prepared: 2026-08-07
- Scope: Domestic 400NG Items 4.5 and 4.13 for the 2026 rate cycle only
- Machine contract: `0006-cf-0004-reweigh-tolerance-dossier.json`

This dossier does not resolve `CF-0004`, register an interpretation, publish a
rule, authorize a charge, or calculate money. It compares the candidate facts
that could select the tariff's “5,000 pounds or less” branch.

## Question and direct source boundary

400NG Item 4.5 makes a fee payable for a lower reweigh only when the loss is:

- less than 150 lb for a shipment weighing 5,000 lb or less; or
- less than 5 percent of the lower net scale weight for a shipment weighing
  more than 5,000 lb.

Item 4.13 requires containerized reimbursement when the new tare is greater
than the original tare and the increase is:

- more than 150 lb for a shipment weighing 5,000 lb or less; or
- at least 5 percent of the overall lower tare scale weight for a shipment
  weighing more than 5,000 lb.

Both provisions leave “shipment weight” undefined. Advisory 23-0004 confirms
lesser-weight invoicing only after tolerance qualification, so it does not make
the lower weight the branch selector. The source basis is `CLM-0023`,
`CLM-0028`, `CLM-0044`, and `CLM-0045`, with the focused search preserved in
`docs/reweigh-tolerance-source-research.md`.

## Candidate comparison

| Candidate | Availability and stability | Source support | Assessment |
|---|---|---|---|
| Final reviewed initial net scale weight | Exists before either tolerance decision; is already an explicit Item 4.5 operand; can be required for both paths | Not expressly named as the branch fact | **Provisional lead.** Stable, common to both rules, and does not depend on the decision's later result |
| Completed reweigh net scale weight | Exists after a complete reweigh; may change when duplicate reweighs are completed | Not expressly named; unavailable during the provisional-only stage | Plausible for Item 4.5, but weaker as a common Item 4 selector |
| Lower initial/reweigh net scale weight | Deterministically available after a complete reweigh | Named as the 5-percent denominator, not as the branch fact; Advisory 23-0004 uses it after qualification | Plausible but result-dependent; the source sequence does not support promoting it to selector |
| Containerized provisional net weight | Exists only when new gross is combined with original tare and may later be corrected | Item 4.13 authorizes it for provisional billing, not branch selection | Reject as a universal selector; temporally stale when the later tare reimbursement is decided |
| Reviewed accepted controlling weight | Could mean the final upstream billed-weight result | No governing source defines this term for the branch | Reject unless an authority defines it; otherwise it hides lower/provisional assumptions behind a mutable label |

## Proposed narrow interpretation

If a local interpretation is approved, use the **final reviewed initial net
scale weight** to select the branch for both Item 4.5 and Item 4.13:

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

All values remain exact decimals in pounds. No rounding is introduced. A
missing, conflicting, unreviewed, constructive-only, or otherwise invalid
initial net result blocks the decision instead of selecting another candidate.

The rationale is limited: initial net is the only candidate that is available
before both tolerance decisions, is explicitly named in Item 4.5's subtraction,
and does not make the branch change when a later result changes. This is an
interpretive inference, not direct tariff text.

## Opposing-side boundary results

`T` means the fee qualifies or reimbursement is required under that candidate;
`F` means it does not. `Init`, `Rew`, `Low`, `Prov`, and `Acc` denote the five
candidates in the comparison above.

### Lower-reweigh fee

| Case | Initial / reweigh / difference (lb) | Material boundary | Init | Rew | Low | Prov | Acc |
|---|---:|---|---:|---:|---:|---:|---:|
| `FEE-001` | 5001 / 4851 / 150 | Candidate facts oppose across 5,000 | T | F | F | F | F |
| `FEE-002` | 5150 / 5000 / 150 | Reweigh and lower are exactly 5,000 | T | F | F | T | F |
| `FEE-003` | 5000 / 4851 / 149 | Exactly 5,000; just below 150 | T | T | T | T | T |
| `FEE-004` | 5000 / 4850 / 150 | Exact 150 is not “less than 150” | F | F | F | T | F |
| `FEE-005` | 5250 / 5000 / 250 | Exact 5 percent is not “less than 5 percent” | F | F | F | F | F |
| `FEE-006` | 5249.99 / 5000 / 249.99 | Just below 5 percent | T | F | F | T | F |
| `FEE-007` | 5000 / 5000 / 0 | Equal reweigh qualifies before tolerance | T | T | T | T | T |

### Containerized reimbursement

| Case | Original / new tare / increase (lb) | Material boundary | Init | Rew | Low | Prov | Acc |
|---|---:|---|---:|---:|---:|---:|---:|
| `REIMB-001` | 2000 / 2150 / 150 | Initial is over 5,000; others exactly 5,000 | T | F | F | F | F |
| `REIMB-002` | 4000 / 4151 / 151 | Provisional alone is over 5,000 | T | T | T | F | T |
| `REIMB-003` | 4000 / 4200 / 200 | Exact 5 percent and over 150 | T | T | T | T | T |
| `REIMB-004` | 4000 / 4199.99 / 199.99 | Just below 5 percent but over 150 | F | T | T | F | T |
| `REIMB-005` | 4000 / 4150 / 150 | Exact 150 and below 5 percent | F | F | F | F | F |
| `REIMB-006` | 4000 / 4000 / 0 | New tare is not greater | F | F | F | F | F |

These cases demonstrate that branch selection is material and that neither
threshold family is uniformly more permissive. The accompanying validator
recomputes every result with `Decimal` and rejects altered boundary outcomes.

## Decision alternatives

### `A_APPROVE_INITIAL_NET_SCOPED` — provisional recommendation

Approve the proposed initial-net selector only for 2026 domestic 400NG Items
4.5 and 4.13. Require reviewed ticket provenance and the full boundary suite.
Reopen immediately if an applicable publisher clarification or contrary source
is archived. This approval would resolve only `CF-0004`; `CF-0001` and
`CF-0003` would still block any unsupported fee amount or billing-code contract.

### `B_APPROVE_LOWER_NET_SCOPED`

Use the final lower net weight. This aligns the selector with the percentage
denominator and eventual lower-weight billing result, but it is weaker on source
sequence and can move the shipment between branches after the reweigh.

### `C_DEFER_FOR_PUBLISHER`

Keep both rules blocked until USTRANSCOM/PPA supplies an amendment, written
clarification, or worked example. This is the conservative external-source-only
choice.

The reweigh-net, provisional-net, and undefined accepted-weight candidates are
documented but are not offered as approval alternatives because they cannot
serve both decisions without an availability, timing, or definition gap.

## Approval and implementation gate

An approval must name the selected alternative, approver and role, decision
date, effective scope, reopening condition, and required tests. Until then:

- `CF-0004` remains open;
- no `INT-` record may be added;
- both affected registry rules remain draft and conflict-blocked; and
- no fee, reimbursement, invoice line, or money result may be produced.

