# Item-Code and Mileage/SIT Source-Currency Research

Status: public-source investigation completed 2026-08-03; interpretation cases
remain open where the authoritative record is incomplete.

## Question and method

This investigation tested whether the 12 August 2022 Item Code Listing and the
undated DPS Mileage Transit Time SIT Tool can govern 2026 domestic DP3 decisions.
It compared:

- the archived source artifacts and their embedded metadata;
- 2026 400NG Item 1.2(c) and DTR Part IV Chapter A-402;
- the legacy USTRANSCOM DP3 public library;
- the new PPA Industry & Government Resource Center; and
- current PPA advisories that identify the authoritative publication surface or
  demonstrate mid-cycle item-code supplements.

Web observations were made on 2026-08-03. Direct downloads from PPA.mil and
media.defense.gov returned HTTP 403 from this environment, and the in-app browser
was unavailable. Those online observations are therefore marked candidate until
the raw page/PDF can be archived. Existing archived XLSX/ZIP/PDF sources remain
unchanged and checksummed.

## Finding 1 — the mileage workbook has a file version marker, not an effective date

The archived `SRC-DP3-MILEAGE-SIT` workbook's `docProps/core.xml` records:

| Property | Value |
|---|---|
| Creator | `SDDC` |
| Last modifier | `Stroot, Sheldon CTR USTRANSCOM J6` |
| Created | `2009-06-12T18:38:05Z` |
| Modified | `2025-09-26T06:57:51Z` |

This metadata is direct evidence about the archived file, not an effective-date
claim. It shows that the workbook predates the 8 December 2025 publication of the
2026 transit tables. The hidden workbook table's 9-day result therefore cannot
override the explicit 2026 table's 18-day result for the tested bracket.

The [PPA Resource Center](https://www.ppa.mil/Industry-Government-Resource-Center/)
still exposes a same-titled mileage/SIT tool as a quick link. This supports
continued operational publication as of retrieval, but the page displays no
version/effective date and the linked copy could not be downloaded for a hash
comparison.

Interpretation status: reviewed for embedded metadata; candidate for current
publication identity; not approved for effective-date or transit selection.

## Finding 2 — the 70-percent calculation still lacks governing authority

The 14 July 2026 DTR Chapter A-402 says direct-delivery SIT may be authorized
after a percentage of Government transit time and directs the reader to “see
solicitation.” It does not state the percentage or rounding rule. The reviewed
2026 400NG and Household Goods Tender text did not supply the missing 70-percent
provision. The archived workbook's `ROUND(transit_days * 0.7, 0)` remains an
implementation expression, not an approved rule.

Interpretation status: `CF-0002` remains open. The explicit 2026 transit table is
the provisional domestic transit source; derived authorized-SIT days remain
blocked.

## Finding 3 — item-code currency is now a publication-location conflict

The 2026 400NG Item 1.2(c) expressly points to the Item Code Listing at the legacy
USTRANSCOM DP3 library. That library still lists the archived 12 August 2022
workbook and no newer same-titled listing was located.

[PPA Advisory 26-0105](https://media.defense.gov/2026/Jul/06/2003957897/-1/-1/0/DOW%20PPA%20PP%20ADVISORY%2026-0105%20PROMOTE%20THE%20OFFICIAL%20DOW%20PPA%20WEBSITE.PDF),
dated 6 July 2026, calls the new PPA website the authoritative, trusted resource
and tells offices to keep materials current with it. The new PPA catalog did not
expose the 2022 Item Code Listing in the searches and catalog pages reviewed.

This does not prove that the 2022 domestic rows were revoked. It does prove that
continued presence on the legacy page is insufficient by itself to establish a
complete 2026 controlled vocabulary after the authority transition.

Interpretation status: `CF-0003` is upgraded from a simple candidate currency gap
to a disputed publication-location gap. Preserve raw billed codes and the 2022
rows, but do not use that workbook alone to approve/reject a 2026 line.

## Out-of-scope corroboration

PPA Advisory 26-0110, dated 15 July 2026, temporarily authorizes Item Code 231A
for specified international air-freight adjustments. International billing is
outside domestic v1. The advisory is recorded only as evidence that PPA may
supplement item-code behavior through dated advisories, so a current domestic
baseline requires an advisory/supersession inventory as well as a workbook.

## Remaining closure evidence

1. Obtain and checksum the PPA-linked mileage/SIT workbook; compare it with
   `SRC-DP3-MILEAGE-SIT` and obtain a publisher-stated effective period.
2. Locate the solicitation provision referenced by DTR A-402 that states the
   applicable SIT percentage and rounding rule.
3. Obtain a current domestic Item Code Listing, explicit continued-applicability
   statement, or complete domestic advisory/supersession chain.
4. Archive PPA Advisory 26-0105 and the relevant PPA catalog snapshot when the
   CDN permits retrieval; until then, keep their claims at candidate status.
