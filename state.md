# Current State

## Status

Active on branch `agent/a402-lifecycle-sit` with draft PR 1. Scope remains
domestic DP3 TSP-to-Government read-only post-audit. M1 is the productive track.
The current publication scope completes the Item 130 authoritative-source pass
and both `CF-0002` transit/SIT source follow-ups.

## Last checkpoint

Archived PCS JTF Advisories 26-0030 and 26-0027 plus historical DTR Appendix
V.J.3 with immutable manifest hashes, derived text, registered locators, and
reviewed claims. Advisory 26-0030 supports the 2026 transit table and its
`desired_pickup_date` selector beginning 2026-05-15. Advisory 26-0027 identifies
the 2026 rate-filing event as the solicitation and places a separate user guide
inside DPS Rate Filing Workbench.

The governing direct-delivery SIT percentage and exact rounding rule were not
located in the public solicitation notice, current or historical 400NG Item 29,
the current Tender, or current International Tender Item 518. Historical DTR
Appendix V.J.3 points to the International Tender without stating the value,
exposing an incomplete or stale cross-reference. The workbook's `0.7` operand
and Excel `ROUND` behavior remain operational observations, not publishable
rules.

The separate Item 130 source pass also remains non-monetary. Four mapping gaps
remain open, including the explicit tension among Item 130F, BOTO criteria, and
the domestic origin/destination listing rows.

## Durable records

- `docs/cf-0002-source-research.md` and its 2026-08-07 JSON companion cover
  seven archived sources and the authenticated-access boundary.
- `docs/item-130-source-research.md` and its decision companion record the four
  unresolved mapping gaps.
- `docs/conflict-register.md`, `docs/source-currency-research.md`, the source
  registry, manifest, and rule registry carry the reciprocal provenance links.
- `scripts/validate_cf_0002_source_research.py` and
  `scripts/validate_item_130_source_research.py` verify the new records and
  their publication gates.

## Registry snapshot

- 16 archived public source versions.
- 48 locators and 61 registered claims.
- Four conflicts: three open and one scoped-resolved.
- Eleven packages: ten published and one draft; 25 rules: 21 published and four
  draft.

## Current safe behavior

- Use the archived 2026 domestic transit table provisionally when desired
  pickup date is on or after 2026-05-15.
- Do not promote the workbook's `0.7` operand or Excel `ROUND` behavior.
- Keep `RULE-DOMESTIC-TRANSIT-TABLE-2026` and
  `RULE-DIRECT-DELIVERY-SIT-DAY-PERCENT` draft, unimplemented, and blocked by
  `CF-0002`.
- Preserve all Item 130 and Item 4 monetary stop gates.
- Do not ingest real shipment files without written authorization and completed
  sanitization.

## Known blockers

- `CF-0002`: obtain an authorized 2026 DPS Workbench solicitation/user-guide
  artifact or equivalent publisher statement that fixes both the percentage
  and exact rounding rule.
- `CF-0001`, `CF-0003`, Decision 0005 Item 130 gaps, `DF-0001`, and the zero-of-25
  authorized historical acceptance prerequisite remain unchanged.
- No authenticated government system was accessed and no government office,
  publisher, Rates Team, or other external party was contacted.

## Next action

With owner approval and authorized access, inspect the 2026 DPS Rate Filing
Workbench materials or request a publisher statement. Otherwise leave
`CF-0002` blocked and move to another bounded M1 source gap.

## Verification status

All 29 repository validators passed on 2026-08-09 before publication. No rule
or money was published.
