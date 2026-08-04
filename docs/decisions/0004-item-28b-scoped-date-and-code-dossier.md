# Decision 0004 Dossier — Item 28B Scoped Date and Item-Code Continuity

- Status: **Proposed — explicit project-owner approval required**
- Prepared: 2026-08-04
- Scope: Domestic 400NG Item 28B extra-delivery shadow rating for the 2026 rate
  cycle only
- Machine contract: `0004-item-28b-proposed-dossier.json`

No interpretation is registered and no Item 28B financial code is authorized by
this dossier.

## Verified evidence

| Source | Version/effective period | Locator | Retrieved | Direct fact |
|---|---|---|---|---|
| `SRC-DP3-2026-400NG` | Published 2025-12-05; 2026-05-15–2027-05-14 | Item 1.2(c), p. 18; Item 28.2–28.3, pp. 35–36 | 2026-08-03 | Extra deliveries are Government-requested additional delivery stops before final delivery; each performed stop earns a stop-off fee. Item 1.2(c) points listed accessorial services to actual pickup date. |
| `SRC-DP3-2026-RATES` | 2026; 2026-05-15–2027-05-14 | `Additional Rates!A1`, `A13:F13` | 2026-08-03 | Row 13 names 28A/28B/28C and supplies 198.50 USD per occurrence; the sheet banner instead says original requested pickup date. |
| `SRC-DP3-ITEM-CODES` | Published 2022-08-12; effective/supersession unstated | `DOM_400NG!A24:Q24`, legends | 2026-08-03 | Row 24 contains `A`, `28B`, `EA`, destination, `SC`, extra-delivery point `AE`, Destination PPSO, approval required. Values are reviewed; 2026 currency is disputed. |
| `SRC-DP3-LIBRARY-SNAPSHOT-2026-08-03` | Snapshot 2026-08-03 | HTML line 4697 | 2026-08-03 | The official legacy library still links the exact 12 August 2022 listing. This proves publication state, not broad legal currency. |

## Conflicts and precedence

`CF-0001` is material. The charge-specific tariff provision and row 24 both
support actual pickup date; the incorporated rate workbook's general banner says
original requested pickup date. Under Decision 0002, the specific tariff is the
provisional lead for date selection, but only an approved interpretation may
enter a published package.

`CF-0003` also remains material. The exact row is archived and still linked by
the archived official library, but its effective and supersession periods are
unstated and the newer PPA publication surface could not be archived. A narrow
decision would not make the complete 2022 listing current.

## Proposed alternative A — approve narrowly

Approve, for Item 28B only through 2027-05-14:

| Field | Proposed value |
|---|---|
| Rate-version date | Actual pickup date |
| Billing item / unit | `28B` / `EA` |
| Rate | 198.50 USD per eligible occurrence |
| Rate reference | `SC` |
| Location | Additional delivery / `AE` |
| Authorization | Reviewed Government request through preapproval or BL block 13; Destination PPSO role where the approval-screen fact applies |
| Eligible occurrence | Performed additional delivery before final delivery |

Item 28A's self-storage-only exclusion is not copied into this proposal: current
Item 28.1 expressly labels that exclusion as applying to Extra Pickup charges.

## Alternative B — defer

Publish no Item 28B money until a current domestic item-code baseline/advisory
chain and an explicit date clarification are archived.

## Exclusions and tests

Neither alternative approves Item 28C diversion, stop-off transportation,
related additional services, SIT, broad item-code validation, dates after
2027-05-14, live submission, or money movement. Alternative A would require all
ten boundary, eligibility, authorization, evidence, Decimal, and tamper tests
listed in the machine dossier before publication.

## Owner decision required

Please explicitly select **A_APPROVE_NARROW** or **B_DEFER**. Until then, status
remains proposed, `CF-0001` and `CF-0003` remain open, no interpretation ID may
be registered, and no Item 28B rating or audit adapter may be implemented.
