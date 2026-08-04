# Decision 0005 — Revised Item 130 Fact Model Approval

- Status: **Ratified**
- Selected alternative: `A_APPROVE_REVISED_FACT_MODEL_ONLY`
- Ratified: 2026-08-04
- Ratified by: project owner through explicit session approval
- Decision type: internal non-monetary schema-design approval
- Interpretation decision ID: none

## Approved scope

The project owner ratified revised Alternative A after reviewing the preserved
version-1 proposal, selecting `B_REVISE_FACT_MODEL`, and reviewing version 2.
This approval authorizes:

1. Five new article-domain logical records:
   `shipment_article`, `article_measurement_observation`,
   `article_condition_observation`, `article_service_context_observation`, and
   `combined_handling_pair_candidate`.
2. Item 130 profiles of canonical `service_performance` and
   `service_approval_event` records instead of duplicate Item 130 tables.
3. Common append-only audit, provenance, sensitivity, sanitization,
   supersession, and correction metadata.
4. Public-source logical-schema amendments and synthetic non-monetary fixtures
   with positive and negative probes.

## Preserved restrictions

This approval does not resolve `CF-0001` or `CF-0003`, approve the 2022 Item 130
listing for 2026, create an interpretation decision, select a rate date or
billing code, accept `EA` as the current billing unit, derive a billable
quantity, apply the 297.78 USD rate, calculate money, reconcile an invoice or
payment, publish a rule package, register an audit adapter, or authorize real
shipment data.

The four tariff-versus-listing gaps and all 18 mandatory boundary-test categories
remain part of the approved non-monetary contract.
