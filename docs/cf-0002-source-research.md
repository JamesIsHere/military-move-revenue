# CF-0002 Local Source Pass

Status: completed 2026-08-07; conflict remains open.

## Outcome

The pass established authoritative support for the 2026 transit-table package
and its date selector. PCS JTF Advisory 26-0030 identifies the attachment as the
2026 USTC Domestic-International Transit Time Tables effective 15 May 2026 and
applies the changes using **desired pickup date**. The draft transit selector now
uses that fact, but remains unpublished and blocked by `CF-0002` pending an
approved scope and boundary tests.

The follow-up identified the solicitation but did not establish the missing
provision. PCS JTF Advisory 26-0027 calls the 2026 rate-filing event “this
solicitation,” identifies its public business-rule set, and says the separate
Rate Filing User Guide is available inside DPS Workbench. The public notice,
2026 400NG, Tender of Service, and current International Tender do not state the
direct-delivery SIT percentage or rounding rule. The official mileage/SIT
workbook uses `0.7` and Excel `ROUND`, but that remains unsupported as governing
authority.

## Archived source and verification

| Source | Version / effective period | Locator | Retrieval and review | Result |
|---|---|---|---|---|
| `SRC-DP3-ADV-26-0030` | Published 2025-12-08; attachment effective from 2026-05-15 | Paras. 1–3 and attachment title, p. 1 | Retrieved 2026-08-07; SHA-256 `D4161CCA…A37FD6A`; complete one-page text and 150-DPI render reviewed | Desired-pickup-date selector and publication identity supported |
| `SRC-DP3-2026-TRANSIT` | Published 2025-12-08; effective from 2026-05-15 | `Appendix L-Domestic!A1:F33` | Retrieved 2026-08-03; archived workbook structurally reviewed | Recorded example remains 18 days |
| `SRC-DP3-MILEAGE-SIT` | Modified 2025-09-26; effective period unstated | `TT`, `MAIN`, `WORK`, and package metadata | Archived 2026-08-03; official URL retrieved again 2026-08-07 | Current download is byte-identical; conflicting 9-day and 70-percent behavior persists |
| `SRC-DTR-IV-A402` | Version 2026-07-14; separate effective period unstated | Para. C.1.b.(1), p. IV-A-402-17 | Retrieved 2026-08-03; text and render reviewed | Percentage delegated to solicitation; no percentage or rounding rule stated |
| `SRC-DP3-ADV-26-0027` | Published 2025-12-04; filed rates cover 2026-05-15 through 2027-05-14 | Paras. 5-11, pp. 1-3 | Retrieved 2026-08-07; SHA-256 `ACAED24A…31986`; all four pages rendered and reviewed | Identifies the annual solicitation, public rule set, and Workbench-only guide boundary |
| `SRC-DTR-IV-VJ3` | Page dated 2011-11-17; effective period unstated | Para. C.5.f.(1), p. IV-V.J.3-17 | Retrieved 2026-08-07; SHA-256 `95377E26…F0D5`; cited page rendered and reviewed | Historical cross-reference says “See the International Tender”; current applicability disputed |
| `SRC-DP3-2026-400NG` | Published 2025-12-05; effective 2026-05-15 through 2027-05-14 | Item 29.1-29.6, p. 37 | Archived 2026-08-03; direct text reviewed | Governs current domestic SIT entry/FADD conditions but states no percentage or rounding rule |

The duplicate 2026-08-07 mileage/SIT download was not retained because its byte
length and SHA-256 exactly matched the existing raw artifact. The repeat
retrieval comparison is registered at `LOC-0046` and `CLM-0059`.

## Interpretation boundary

- `RULE-DOMESTIC-TRANSIT-TABLE-2026` remains draft, not implemented, and blocked.
- `RULE-DIRECT-DELIVERY-SIT-DAY-PERCENT` remains draft, not implemented, and blocked.
- The annual solicitation was located. Its public notice and public business
  rules do not expose the referenced percentage or rounding provision.
- The only identified nonpublic surface is the DPS Rate Filing Workbench guide;
  it was not accessed because authenticated-system access requires approval.
- No financial result, billing quantity, rate, or audit adapter was produced.
- No government office, publisher, rates team, or other external party was contacted.

The machine-readable checkpoint is
`docs/cf-0002-source-research-2026-08-07.json`.
