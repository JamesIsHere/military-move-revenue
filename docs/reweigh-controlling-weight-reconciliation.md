# Post-Reweigh Controlling-Weight Reconciliation

## Objective

Separate the governing questions in the 2026 reweigh text before implementing a
controlling-weight, fee, refund, or reimbursement rule. This review covers
complete reweighs, duplicate reweighs, and the containerized provisional-weight
path. It does not approve a monetary calculation.

## Source record

All three raw artifacts were retrieved and checksummed on 2026-08-03. The cited
pages were rendered and visually checked on 2026-08-03 against the derived text.

| Source | Version and effective period | Reviewed locator | Role |
|---|---|---|---|
| `SRC-DP3-2026-400NG` | Published 2025-12-05; effective 2026-05-15 through 2027-05-14 | Item 4.5, p. 19; Items 4.11-4.13, pp. 22-23; Item 4 Note 2, p. 23 | Tariff fee eligibility, billed-weight subsets, refund gates, containerized correction, duplicate reweighs |
| `SRC-DP3-2026-TOS-C1` | Published 2026-02-18; effective 2026-05-15 through 2027-05-14 | Weighing Shipments 8.a.(2)(c)-(d), printed p. 20 | General lower-weight invoicing and post-invoice refund obligation |
| `SRC-DTR-IV-A402` | Publication 2026-07-14; effective period unstated | Section D.7.b, p. IV-A-402-20 | Operational DPS facts and ticket-submission evidence |

Interpretation status: direct claims are `reviewed`. The 5,000-lb tolerance
branch input remains `disputed` under `CF-0004`.

## Normalized questions

| Question | Governing claims | Reconciliation |
|---|---|---|
| Which completed reweigh weight is invoiced when it is lower than the initial weight? | `CLM-0024`, `CLM-0030` | The Tender states the general lower-of-two obligation. Item 4.11(d) states the within-tolerance subset and does not direct use of a higher weight outside that subset. No direct conflict is recorded. |
| Does a lower reweigh make the reweigh fee payable? | `CLM-0023` | Separate fee-eligibility question. A lower weight qualifies only within the stated tolerance. This does not determine the controlling billed weight. |
| What if several reweighs exist? | `CLM-0029` | Use the lowest net scale reweigh weight for the DPS update and the fee test. Preserve every observation rather than overwriting a latest weight. |
| What if only a new gross exists for containerized HHG? | `CLM-0027` | Calculate a provisional new net as new gross minus original tare and invoice the lesser weight. It is not a completed reweigh determination. |
| What happens when the later new tare arrives? | `CLM-0028` | Create a later correction/reimbursement decision; do not rewrite the provisional result. The applicable 5,000-lb branch input is unresolved. |
| What happens if the reweigh occurs after initial invoicing? | `CLM-0026`, `CLM-0031` | Preserve the original invoice and add a supplemental refund/adjustment history for reduced affected charges. |
| Which operational evidence must be preserved? | `CLM-0026`, `CLM-0032` | Preserve gross, tare, net, reweigh date, ticket reference/copy, DPS update, PPSO delivery, and billing-hold/refund events. |

## Cross-source conclusion

No new 400NG-versus-Tender conflict is required for the general lower-weight
obligation. The statements answer different scopes:

- the Tender supplies the general performance and invoicing obligation;
- Item 4.5 determines whether the reweigh fee itself is payable;
- Item 4.11 adds within-tolerance, evidence, and constructive-weight conditions;
- Item 4.12 governs refund workflow and billing holds;
- Item 4.13 governs the containerized provisional and later-correction path; and
- Note 2 governs duplicate reweigh observations.

None of the reviewed text affirmatively requires invoicing a higher weight where
another provision requires the lower weight.

## Material ambiguity - CF-0004

Items 4.5 and 4.13 split tolerance behavior at 5,000 pounds but do not identify
which weight fact selects the branch. Candidate facts include the initial net,
reweigh net, lower net, provisional net, or another shipment weight. The choice
can change fee or reimbursement eligibility near the boundary.

Interim behavior:

- do not publish either tolerance-dependent decision;
- preserve every initial, reweigh, provisional, gross, tare, and net observation
  with explicit units and provenance;
- allow nonproduction candidate evaluations only when the branch fact is labeled
  as an unresolved assumption; and
- do not let the ambiguity block the general lower-weight or duplicate-reweigh
  observation model.

Closure requires a governing amendment/advisory, publisher clarification, or a
scoped approved interpretation identifying the 5,000-lb branch fact, followed by
tests that straddle the boundary.

## Implementation boundaries

Future implementation must remain four separate decisions:

1. completed-reweigh controlling weight;
2. reweigh-fee eligibility and tolerance;
3. containerized provisional weight and later correction; and
4. refund/reimbursement workflow and charge allocation.

The first can proceed from reviewed claims without CF-0004. The second and the
tolerance-dependent part of the third must remain blocked. Item-code and rate
selection remain separately gated by CF-0001 and CF-0003 where applicable.
