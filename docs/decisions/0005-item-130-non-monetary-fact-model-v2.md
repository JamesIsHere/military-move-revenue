# Decision 0005 Dossier v2 — Item 130 Non-Monetary Fact Model

- Status: **Revised proposal — project-owner review required**
- Prepared: 2026-08-04
- Revision basis: owner selected `B_REVISE_FACT_MODEL`
- Machine contract: `0005-item-130-fact-model-dossier-v2.json`
- Preserved base: `0005-item-130-fact-model-dossier.json`, SHA-256
  `68B5A485FF086F02DE466606E5A2FAE55462D40B8AE21020C3AD6F08AF435C4E`

This revision changes architecture only. The source basis, ten tariff
classifications, four source gaps, 18 mandatory test categories, open conflicts,
and financial prohibitions remain exactly as defined in version 1.

## What changed after review

Version 1 proposed seven Item 130-specific entities. Review identified possible
duplication of canonical service performance and approval records and did not
state append-only status behavior strongly enough.

Version 2 instead proposes five new article-domain logical records:

1. `shipment_article`
2. `article_measurement_observation`
3. `article_condition_observation`
4. `article_service_context_observation`
5. `combined_handling_pair_candidate`

It profiles, rather than duplicates, two existing canonical entities:

- `service_performance` records planned or completed loading, unloading, shuttle
  transload, and handling/blocking.
- `service_approval_event` records Government preapproval against the stable
  profiled performance.

The service-performance profile preserves an unmapped candidate family while
`CF-0001` and `CF-0003` remain open. `service_definition_id`, quantity, billing
code, rate version, and amount are prohibited. The approval profile preserves
raw approver-role text; it does not accept the disputed 2022 origin/destination
screen representation as a current controlled mapping.

## Append-only behavior

Every new entity and profile inherits identity, audit, provenance, sensitivity,
sanitization, supersession, and correction metadata. Status changes never update
a row in place. They append an event or create a new record that directly
supersedes the prior version. A current status is a derived view over the valid
supersession chain.

This applies to classification review, measurement review, condition/context
observations, performance, pairing review, and approval decisions. The original
observation and every correction remain reproducible.

## Preserved no-money boundary

Version 2 still does not approve the 2022 Item 130 listing, a rate-date fact,
billing code, `EA` unit, origin/destination mapping, combined-service quantity,
297.78 USD rate, expected amount, reconciliation, rule package, or audit adapter.
It creates no interpretation decision ID and uses no real shipment data.

## Revised proposed decision

Alternative **A_APPROVE_REVISED_FACT_MODEL_ONLY** approves the five new logical
records, two existing-entity profiles, common append-only metadata, inherited
source/evidence/test contracts, and synthetic non-monetary fixture development.
It approves logical contracts, not physical table implementation.

Alternative **B_REVISE_AGAIN** requests another architecture or contract change.

If revised Alternative A is approved, the next increment is to amend the public-
source logical schema and add a synthetic Item 130 fact fixture with paired
negative probes. Financial work remains separately blocked.
