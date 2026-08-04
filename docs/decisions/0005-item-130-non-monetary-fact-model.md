# Decision 0005 Dossier — Item 130 Non-Monetary Fact Model

- Status: **Proposed — project-owner review required**
- Prepared: 2026-08-04
- Scope: Domestic 400NG Item 130 fact and evidence model only
- Machine contract: `0005-item-130-fact-model-dossier.json`

The project owner authorized preparation of this dossier. That authorization is
not field-level approval and does not resolve a billing interpretation. This
dossier publishes no rule, rate selection, billing mapping, quantity, expected
amount, reconciliation, or audit adapter.

## Why model this now

The current tariff directly defines ten article classifications, conditional
measurements and states, Government preapproval, performed handling, and several
exclusions. Those facts can be collected and reviewed independently of the open
rate-date and item-code conflicts. Modeling them now isolates the larger Item
130 fact surface before any monetary decision.

## Source basis

| Source | Version/effective period | Locator | Retrieved | Use in this dossier |
|---|---|---|---|---|
| `SRC-DP3-2026-400NG` | Published 2025-12-05; 2026-05-15–2027-05-14 | Item 130, pp. 54–55 | 2026-08-03 | Governing article, measurement, approval, handling, and exclusion facts |
| `SRC-DP3-ITEM-CODES` | Published 2022-08-12; effective/supersession unstated | `DOM_400NG!A53:Q118`, legends | 2026-08-03 | Candidate future mapping observations only; 2026 currency remains disputed |
| `SRC-DP3-LIBRARY-SNAPSHOT-2026-08-03` | Snapshot 2026-08-03 | HTML line 4697 | 2026-08-03 | Proves the exact listing remained published at retrieval, not that it governed 2026 |

The machine dossier gives every proposed field a logical type, cardinality,
evidence requirement, provenance ID, and interpretation status. Internal
identity, review, and evidence-link fields cite the ratified goal and logical
schema rather than being presented as Government tariff requirements.

## Proposed entity boundary

| Entity | Purpose |
|---|---|
| `shipment_article` | Keeps the observed article separate from its reviewed 130A–130J classification candidate. |
| `article_measurement_observation` | Preserves exact length, width, height, volume, screen size, or engine displacement and the measurement method. |
| `article_condition_observation` | Records assembled, flat-screen, one-person hand-carry, and standard-carton facts. |
| `article_service_context` | Records Code 2, crating, BOTO, and over-14-foot HHG co-move context without treating them as billing outcomes. |
| `article_handling_event` | Represents immutable loading, unloading, shuttle transload, handling, SIT, and TSP-convenience observations. |
| `combined_handling_occurrence_candidate` | Links a proposed loading/unloading pair for human review; it is not billable quantity. |
| `item_130_preapproval_event` | Preserves the Government decision, chronology, observed approver role, and reviewed evidence separately from performance. |

Unknown and conflicting facts remain explicit. Similar-looking unlisted articles
cannot be auto-classified. Exact measurements use decimal strings with explicit
units; AI extraction may propose facts but cannot approve classification or
financial use.

## Preserved source gaps

The tariff and candidate listing are not silently merged:

1. Tariff 130B includes riding lawnmowers, including stand-on models; listing
   rows 53–118 contain no lawnmower description.
2. Tariff 130E includes several over-14-foot watercraft types when moved with
   HHG; listing rows 89–90 describe only boats over 14 feet.
3. Tariff 130F directs boat trailers to the BOTO program, while listing rows
   91–92 present dHHG origin/destination representations.
4. The tariff describes one charge for each combined loading/unloading service;
   the listing presents separate origin and destination rows.

These are fact-model and future-mapping review points. They do not authorize a
code, quantity, or calculation. `CF-0001` and `CF-0003` remain open for Item 130.

## Proposed decision

Alternative **A_APPROVE_FACT_MODEL_ONLY** approves the seven entity boundaries,
field provenance, evidence targets, and 18-test synthetic boundary contract. It
keeps every financial output prohibited and every recorded conflict or gap open.

Alternative **B_REVISE_FACT_MODEL** requests changes to the entity, field,
cardinality, or evidence contracts before logical-schema fixtures are added.

No interpretation decision ID will be registered under either alternative.
After owner review, the next allowed increment under Alternative A is a
synthetic fact fixture plus negative probes. Monetary implementation requires a
separate, later source decision.
