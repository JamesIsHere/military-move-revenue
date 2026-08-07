# Reweigh-Tolerance Branch Source Research

Status: focused authoritative-source pass completed 2026-08-07; the pass found
no source answer. Decision 0006 / `INT-0003` later supplied a scoped owner-
approved interpretation for the 2026 cycle.

## Question

Which weight fact selects the 5,000-pound branch in 400NG Item 4's reweigh-fee
and containerized-reimbursement tolerance tests: initial net, reweigh net,
lower net, provisional net, or another accepted shipment weight?

## Method and source boundary

The search prioritized official USTRANSCOM tariffs and advisories, current and
historical DTR material, and public CBCA/GAO decisions. Search-engine extracts
and accessible online text were used only to locate candidates. A claim was not
promoted unless its authoritative artifact was already archived or was newly
downloaded, checksummed, text-extracted, and visually reviewed.

The legacy `www.ustranscom.mil` advisory link returned a branded HTTP 404. The
same catalog path on `business.ustranscom.mil` returned the authoritative PDF;
the working business-host URL is the registered canonical retrieval route.

## Newly archived official artifacts

| Source | Publication/effective period | Locator | Archive proof | Finding |
|---|---|---|---|---|
| `SRC-DP3-ADV-23-0004` | Published 2022-10-13; applies to pickup dates from 2022-10-24 | Paras. 1 and 3.4, p. 1 | 192,535 bytes; SHA-256 `F312A14DB1DCDC645A4E11E22A61922999448B57E1F4D87099134576BAE4BF5B` | USTRANSCOM requires lesser-weight invoicing if the reweigh first falls within the tariff tolerance. It does not name the fact selecting the tolerance branch. |
| `SRC-DP3-ADV-22-0097B` | Published 2022-10-04; proposed 2023 rules effective 2023-05-15 | Paras. 4, 9, and 10-11, pp. 1 and 5-6 | 349,158 bytes; SHA-256 `CAC3185FD8571DD1BB2225B1D8F7B615343E8E25791666AC7C88DF30AD11EE08` | USTRANSCOM solicited service comments, said approved final documents would be posted, and said replies would not be sent. It contains no reweigh interpretation or worked example. |

## Existing archived artifact re-reviewed

The archived 2026 400NG List of Changes, p. 8, records this Item 4 sequence:

- 3 June 2022: replaced “net” with “tare” in the reweigh provisions;
- 20 July 2022: corrected the language by replacing “tare” with “net”; and
- 18 October 2022: “Adjusted reweigh language.”

This official version history establishes that USTRANSCOM revisited the weight
terminology and later billing workflow. It does not identify whether initial,
reweigh, or lower weight selects the 5,000-pound branch.

## Other official material inspected online

- [2024 400NG](https://www.business.ustranscom.mil/dp3/docs/otherpdfs/0820%2B2024_Business_Rules/2024%20400NG%2029%20Dec%2023%20v1.pdf),
  [2021 400NG Change 1](https://www.business.ustranscom.mil/dp3/docs/otherpdfs/0300%2B2021_Business_Rules/2021%20400NG%20Change%201.pdf), and
  [IT-26 Change 1](https://media.defense.gov/2026/Apr/20/2003915135/-1/-1/0/IT-26%20CHANGE%201%20%2804%20MAR%202026%29.PDF) repeat the unnamed
  “shipments weighing” boundary. These online observations were not promoted
  into archived source claims.
- [DTR Part IV Chapter 402](https://www.ustranscom.mil/dtr/part-iv/dtr_part_iv_402.pdf)
  covers reweigh ordering, DPS facts, tickets, and forms but does not state the
  fee-tolerance selector.
- Public GAO decisions located in the pass enforce lower-weight billing or
  address weight-ticket validity, but none interprets the modern 150-pound/5%
  branch. They were not promoted as `CF-0004` evidence.

## Result

No retrieved authoritative source identifies the 5,000-pound branch fact.
Advisory 23-0004 cannot safely be read as selecting lower weight for the branch:
its wording assumes the tolerance test has already been satisfied and then
directs which weight to invoice. At completion of this source-only pass, the
conservative behavior remained:

- preserve every candidate weight fact and provenance;
- do not publish the reweigh-fee tolerance selector;
- do not publish the tolerance-dependent containerized reimbursement selector;
  and
- do not silently choose a branch at exactly or across 5,000 pounds.

## Subsequent scoped interpretation

The project owner later approved Decision 0006 Alternative A. `INT-0003` uses
the final reviewed initial net scale weight for Items 4.5 and 4.13 only for
actual pickup dates 2026-05-15 through 2027-05-14. That approval does not change
the search result: no retrieved source expressly names the selector. See
`docs/decisions/0006-cf-0004-initial-net-scoped.md` for scope, exclusions, and
reopening conditions.

## Remaining closure evidence

1. A USTRANSCOM/PPA amendment, advisory, written Rates Team clarification, or
   worked example explicitly naming the branch fact.
2. Otherwise, an approved scoped interpretation with opposing-side boundary
   cases, exactly 5,000 pounds, strict `< 150` and `< 5%` fee comparisons, and
   the containerized `> 150` and `>= 5%` reimbursement comparisons.
