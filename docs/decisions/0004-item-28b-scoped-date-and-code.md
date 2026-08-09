# Decision 0004 — Item 28B Scoped Date and Item-Code Continuity

- Status: Accepted
- Date: 2026-08-04
- Approver: Project owner, by explicit agreement with recommended Alternative A
- Scope: Domestic 400NG Item 28B extra-delivery shadow rating for the 2026 rate
  cycle only
- Proposal preserved at: `0004-item-28b-scoped-date-and-code-dossier.md` and
  `0004-item-28b-proposed-dossier.json`

## Decision

The project owner selected `A_APPROVE_NARROW`. For Item 28B only from
2026-05-15 through 2027-05-14, actual pickup date selects the rate version and
the archived `DOM_400NG!A24:Q24` fields may be combined with current 400NG Item
28 eligibility and `Additional Rates!A13:F13`.

| Field | Approved value |
|---|---|
| Rate-version date | Actual pickup date (`A`) |
| Billing item / unit | `28B` / `EA` |
| Rate | 198.50 USD per eligible occurrence |
| Rate reference | `SC` |
| Location | Additional delivery / `AE` |
| Approval screen | Destination PPSO |
| Approval required | Yes; reviewed preapproval or Government request recorded in BL block 13 |
| Eligible occurrence | Performed additional delivery before final delivery |

Under Decision 0002, charge-specific tariff Item 1.2(c) and row 24 support
actual pickup date over the rate workbook's general original-requested-pickup
banner within this narrow scope. The archived official library still links the
exact 2022 listing, and no contrary Item 28B source is archived. This approved
interpretation is `INT-0002`.

## Exclusions and reopening

This decision does not approve Item 28A, Item 28C diversion, transportation via
stop-offs, related additional services, SIT, broad 2022 item-code validation,
dates after 2027-05-14, live submission, or money movement. `CF-0001` and
`CF-0003` remain open broadly. Reopen `INT-0002` if a contrary or superseding
source is archived.

## Publication gate

Approval authorizes registration of an immutable draft package and its source,
eligibility, and exact-charge rules. It does not make those rules published.
Publication requires every mandatory test in the preserved proposal, complete
provenance/evidence output, exact Decimal arithmetic, and result-tamper rejection.
