# Item 130 Source-Gap Research

Status: focused authoritative-source pass completed 2026-08-07. No recorded
gap was closed and no monetary or billing mapping was approved.

## Question

Can public authoritative material reconcile four differences between 2026
400NG Item 130 and the USTRANSCOM Item Code Listing published 12 August 2022?

1. Item 130B names riding lawnmowers, but the listing has no lawnmower row.
2. Item 130E names five watercraft types, but its two rows say only “boats.”
3. Item 130F refers boat trailers to BOTO, but the listing presents domestic
   origin and destination rows.
4. Item 130 states one charge per combined loading-and-unloading service, but
   every listing description has separate origin and destination rows.

## Source boundary

The findings use only archived and checksummed USTRANSCOM artifacts:

| Source | Version and effective period | Locator | Retrieval | Status |
| --- | --- | --- | --- | --- |
| `SRC-DP3-2026-400NG` | Published 2025-12-05; effective 2026-05-15–2027-05-14 | Item 130, pp. 54–55; Code B/H definitions, pp. 11–12; Items 300–301, p. 63 | 2026-08-03 | Governing text reviewed; internal tension remains |
| `SRC-DP3-ITEM-CODES` | Published 2022-08-12; effective/supersession period unstated | `DOM_400NG!A53:Q118`, focused rows 53–70 and 79–92; legends `A151:L166` | 2026-08-03 | Values reviewed; currency and mapping disputed |
| `SRC-DP3-LIBRARY-SNAPSHOT-2026-08-03` | Publication state archived 2026-08-03 | Household Goods link titled `Item Code Listing (12 Aug 2022).zip` | 2026-08-03 | Proves the observed link, not broad 2026 currency |

Official USTRANSCOM library, tariff, advisory, and historical business-rule
searches were also run for `Item 130`, `130B`, `130E`, `130F`, `BOTO`, the item
listing, and the referenced `TSP OTO User Guide`. The search found tariff copies
and historical tariffs, but no superseding listing, advisory, worked example,
or accessible guide that reconciled the gaps. Search snippets and unarchived
copies were used only as candidate locators and were not promoted into claims.

## Findings

| Gap | Result | Source-backed finding |
| --- | --- | --- |
| `GAP-130-LAWNMOWER-ROW` | Open | Item 130B expressly includes riding lawnmowers, including stand-on models. Complete inspection of listing rows 53–70 finds no lawnmower description. No current row or crosswalk was located. |
| `GAP-130E-SUBTYPE-ROWS` | Open | Item 130E expressly names boats, dinghies, sculls, skiffs, and row boats over 14 feet when shipped with HHG. Rows 89–90 say only “boats.” No authority says that description is an umbrella for the other subtypes. |
| `GAP-130F-BOTO-BOUNDARY` | Open; narrowed to an explicit conflict | Item 130F labels boat trailers at most 16 feet and refers them to BOTO. Code B/H definitions and Item 301 instead describe BOTO using over-14-foot or over-dimension boat units and the HHG TSP’s agreement. Rows 91–92 also expose domestic origin/destination representations. Trailer length alone cannot select the program. |
| `GAP-130-COMBINED-VS-OD` | Open | Item 130 allows one charge per required combined loading-and-unloading service. The listing pairs every description as separate origin and destination rows. No source identifies those rows as approval routing, alternatives, or separate billable occurrences. |

The 130F pass is a narrowing, not a resolution. Reading either the Item 130F
parenthetical or Item 301 in isolation would discard contrary governing text.
Both claims therefore remain visible for publisher or approved human review.

## Safe boundary

- Do not map lawnmowers by similarity to another 130B description.
- Do not treat “boats” as an approved 130E umbrella term.
- Do not select BOTO or dHHG Item 130F from trailer length alone.
- Do not infer billable quantity or two charges from origin/destination rows.
- Do not publish an Item 130 rule package, expected amount, or audit adapter.

The machine-readable record is
`docs/decisions/0005-item-130-source-research-2026-08-07.json`. A Rates Team
request would be an external action and was not sent.

## Closure evidence still needed

An authoritative current item-code artifact, an explicit continuation and
crosswalk statement, a governing advisory, or written publisher clarification
must answer the row mappings, 130F program boundary, and combined-service row
semantics. Any later financial contract also remains subject to `CF-0001` and
`CF-0003`, explicit approval, and deterministic boundary tests.
