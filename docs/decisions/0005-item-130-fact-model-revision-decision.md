# Decision 0005 Review — Revise Item 130 Fact Model

- Status: **Accepted revision request**
- Selected alternative: `B_REVISE_FACT_MODEL`
- Decided: 2026-08-04
- Decided by: project owner through explicit session agreement
- Decision type: internal schema-design review; not a Government-source
  interpretation

## Owner direction

After reviewing Alternative A, the project owner agreed with the recommendation
to revise the fact model and instructed the project to proceed.

## Accepted revision scope

1. Preserve the original proposed dossier unchanged as version 1.
2. Distinguish genuinely new article-domain records from profiles of the
   existing `service_performance` and `service_approval_event` records.
3. Apply record-audit and supersession metadata to every new record and profile.
   A status change creates a new record; it never overwrites the prior status.
4. Clarify that approving a revised Alternative A would approve logical schema
   contracts and synthetic tests, not physical tables or financial behavior.
5. Preserve all four source gaps, all open conflicts, and every no-money gate.

## Explicit non-effects

This review does not create an interpretation decision ID, approve the 2022
listing for Item 130, select a rate date or code, produce billable quantity or
money, publish a rule package, add an audit adapter, or authorize real shipment
data.

The revised version remains proposed until the project owner separately reviews
and approves or rejects its new Alternative A.
