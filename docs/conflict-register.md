# Source Conflict Register

This register applies Decision 0002. It preserves competing claims and version
gaps; it is not an approval log. All artifacts were retrieved on 2026-08-03 and
remain archived under their manifest source IDs.

## Summary

| Case | Question | Type | Material effect | Status |
|---|---|---|---|---|
| `CF-0001` | Which event date selects 2026 SIT/accessorial rate tables? | Direct/scope conflict | Rate-version selection and money | Open broadly; Item 28B-only exception approved by `INT-0002` |
| `CF-0002` | Which domestic transit table applies for 2026, and may it drive authorized SIT days? | Version/numeric conflict | RDD, transit days, SIT entitlement | Open — narrowed; 70% authority unresolved |
| `CF-0003` | Is the 12 August 2022 item-code listing still applicable to 2026 shipments? | Publication-location and currency gap | Billing-code and evidence validation | Open broadly; Item 28A/28B-only exceptions approved by `INT-0001`/`INT-0002` |
| `CF-0004` | Which weight fact selects the 5,000-lb reweigh-tolerance branch? | Material input ambiguity | Reweigh-fee and containerized reimbursement eligibility | Resolved for 2026 scope by `INT-0003`; reopen on contrary or later-cycle authority |

## CF-0001 — SIT/accessorial table-selection date

### Claims

| Claim | Source provenance | Claim | Status |
|---|---|---|---|
| `CLM-0001` | `SRC-DP3-2026-400NG`; publication 2025-12-05; effective 2026-05-15–2027-05-14; Item 1.2(c), p. 18 | SIT and accessorial services identified in the Item Code Listing use tables in effect on actual pickup date. | Reviewed |
| `CLM-0002` | `SRC-DP3-2026-RATES`; version 2026; effective 2026-05-15–2027-05-14; `Base Point City!A1`, `Geographical Schedule!A1`, `Additional Rates!A1`, and `Accessorials!A1` | Each sheet displays “Based on Original Requested Pickup Date” beneath its effective date. | Reviewed |

### Precedence analysis

The normalized question is the rule that selects a numeric table version. Under
Decision 0002, the tariff controls date selection and the incorporated workbook
supplies values. Item 1.2(c) is specific to SIT/accessorial services, while the
workbook banner is general across rate sheets. `CLM-0001` is therefore the
provisional lead, but the conflict remains material because the rate workbook is
an incorporated tariff component and the exception itself points to the Item
Code Listing.

### Interim behavior

- Do not publish an SIT/accessorial rate-version selector.
- Preserve original requested pickup and actual pickup as separate facts.
- Permit provisional schema and test design using `CLM-0001`, clearly marked
  disputed and nonproduction.
- Exception: Decision 0004 / `INT-0002` approves actual pickup date only for
  the 2026 Item 28B draft package. It does not resolve another accessorial.

### Evidence required to close

- A current applicable Item Code Listing with its effective/supersession period.
- Applicable 2026 amendments or advisories clarifying the workbook banner or
  Item 1.2(c).
- A scoped interpretation approval and boundary tests spanning a rate-cycle
  change between requested and actual pickup.

Affected discoveries: `DISC-0080`, `DISC-0085`.

## CF-0002 — Domestic transit and authorized-SIT-day source

### Claims

| Claim | Source provenance | Claim | Status |
|---|---|---|---|
| `CLM-0003` | `SRC-DP3-2026-TRANSIT`; publication 2025-12-08; effective from 2026-05-15; `Appendix L-Domestic!A1:F33` | Domestic transit days are selected by mileage and shipment-weight bands; at 751–1,000 miles and 4,000–7,999 lbs the result is 18 days (`A5:E5`). | Reviewed |
| `CLM-0004` | `SRC-DP3-MILEAGE-SIT`; version/effective period unstated; `TT!A1:F21`, with lookup formula at `WORK!I4` | The hidden tool table supplies 9 days for the same mileage/weight bracket (`TT!A5:E5`). | Reviewed value; disputed applicability |
| `CLM-0005` | `SRC-DP3-MILEAGE-SIT`; `MAIN!G9:H10` and `WORK!G5:I5` | For the tool's stated non-Alaska direct-delivery scope, displayed authorized SIT day is Excel `ROUND(transit_days × 0.7, 0)`. | Reviewed expression; disputed authority |
| `CLM-0007` | `SRC-DP3-MILEAGE-SIT`; archived XLSX `docProps/core.xml` | The file was last modified `2025-09-26T06:57:51Z` by a named USTRANSCOM J6 contractor; the metadata does not state an effective period. | Reviewed direct metadata |
| `CLM-0008` | `SRC-DTR-IV-A402`; 14 July 2026 version, Chapter A-402, para. C.1.b.(1), p. IV-A-402-17 | Direct-delivery SIT may be authorized after a percentage of Government transit time, but the DTR says “see solicitation” and does not state the percentage. | Reviewed direct text |
| `CLM-0009` | `SRC-PPA-RESOURCE-CENTER`; quick links observed 2026-08-03 | The authoritative PPA resource surface currently exposes a same-titled “DPS Mileage Transit Time SIT Tool” without a displayed publication or effective date. | Candidate online observation; raw page capture pending |

### Precedence analysis

For 2026 domestic transit days, `CLM-0003` has an explicit publication and
effective date and is the provisional lead. The mileage tool is an
official-operational implementation aid last modified in September 2025, before
the 2026 transit table was published. Its hidden `TT` values therefore cannot
supersede the explicit 2026 table. Current PPA publication supports continued
operational availability of a same-titled tool, but does not supply an effective
period or establish byte identity with the archived copy. The DTR confirms that
some solicitation percentage exists, yet does not state 70 percent. This
resolves provisional 2026 transit-table selection for schema work but does not
authorize the tool's 70-percent SIT expression.

### Interim behavior

- Use the 2026 transit workbook for provisional domestic transit schema and
  synthetic transit tests.
- Do not use the hidden `TT` table in a published rule package.
- Do not approve the 70-percent authorized-SIT-day expression until an applicable
  governing source or current version metadata confirms it.

### Evidence required to close

- A downloadable/checksummable copy of the PPA-linked mileage/SIT tool or a
  publisher statement identifying its version and effective period.
- The referenced solicitation provision or other governing text stating the SIT
  percentage and its exact rounding rule.
- Regression tests comparing applicable transit versions and SIT boundaries.

Affected discoveries: `DISC-0056`, `DISC-0064`, `DISC-0073`, `DISC-0088`–`DISC-0091`.

## CF-0003 — Item-code listing currency

### Claims and gap

`CLM-0006` comes from `SRC-DP3-ITEM-CODES`, version 2022-08-12, effective and
supersession periods unstated, `DOM_400NG!A4:Q149` and legends `A151:L166`. It
defines domestic code, unit, location, date-basis, EDI-note, and approval fields,
including SIT rows 185A/B, 210A–F, and 226A. No conflicting listing is archived,
but continued applicability to 2026 is unproved.

| Claim | Source provenance | Claim | Status |
|---|---|---|---|
| `CLM-0010` | `SRC-DP3-2026-400NG`; publication 2025-12-05; Item 1.2(c), p. 18 | The 2026 tariff expressly refers to the Item Code Listing at the legacy USTRANSCOM DP3 library when identifying SIT/accessorial date treatment. | Reviewed direct text |
| `CLM-0011` | Legacy USTRANSCOM DP3 library; observed 2026-08-03 | The legacy page still offers “Item Code Listing (12 Aug 2022)” and no newer same-titled listing was located there. | Candidate historical observation retained; superseded for direct page evidence by archived `CLM-0037` |
| `CLM-0012` | `SRC-PPA-ADV-26-0105`, 6 July 2026, para. 1; `SRC-PPA-RESOURCE-CENTER` catalog observed 2026-08-03 | Advisory 26-0105 identifies PPA.mil as the authoritative current resource surface, while the PPA business-rule catalog search did not expose the 2022 Item Code Listing. | Candidate publication-location conflict; raw PPA artifacts pending |
| `CLM-0034` | `SRC-DP3-2026-400NG`; publication 2025-12-05; effective 2026-05-15-2027-05-14; Item 28.1 and 28.3, pp. 35-36 | Item 28A applies to a Government-ordered completed additional pickup after the first, excluding the sole self-storage/mini-warehouse pickup or delivery case. | Reviewed direct text |
| `CLM-0035` | `SRC-DP3-2026-RATES`; version 2026; effective 2026-05-15-2027-05-14; `Additional Rates!A1`, `A13:F13` | The Item 28A/28B/28C rate is 198.50 USD per occurrence. | Reviewed direct workbook value and text |
| `CLM-0036` | `SRC-DP3-ITEM-CODES`; publication 2022-08-12; effective/supersession unstated; `DOM_400NG!A4:Q4`, `A23:Q23`, legends `B154:L166` | Item 28A uses requested-pickup date basis, `EA`, `SC`, `AB`, the Origin PPSO approval screen, and requires approval. | Reviewed direct workbook values; approved only within `INT-0001` scope |
| `CLM-0037` | `SRC-DP3-LIBRARY-SNAPSHOT-2026-08-03`; snapshot/retrieval 2026-08-03; HTML line 4697 | The archived official library page links the exact `Item Code Listing (12 Aug 2022).zip` artifact. | Reviewed direct archived HTML |

PPA Advisory 26-0110 separately demonstrates that item-code behavior can be
supplemented by a 2026 advisory. That advisory concerns international air freight
and is outside domestic v1, so it is contextual evidence about the publication
mechanism only and is not incorporated into a domestic rule.

### Interim behavior

- Use the fields and values for provisional schema design only.
- Do not reject or approve a 2026 invoice line solely from this version.
- Preserve original external codes even when a current validation set is absent.
- Exception: Decision 0003 / `INT-0001` approves only the Item 28A row for the
  2026 extra-pickup shadow-rating package. It does not approve broad item-code
  validation.
- Exception: Decision 0004 / `INT-0002` approves only Item 28B row 24 for the
  2026 extra-delivery draft package. Publication still requires implementation
  and all mandatory tests.

### Scoped decision

The project owner approved `INT-0001` on 2026-08-03. The current tariff names
Item 28A and its eligibility, the current rate workbook names Item 28A and its
198.50 USD-per-occurrence rate, and the archived official library snapshot still
publishes the exact 2022 listing that supplies the remaining row-level billing
contract. This combined evidence is sufficient for Item 28A only. The complete
decision, exclusions, and mandatory tests are recorded in Decision 0003.

### Evidence required to close

- A current official domestic item-code artifact, an explicit “still current”
  statement, or a complete baseline-plus-advisory supersession chain through the
  applicable shipment period.
- Comparison of changed/retired codes and regression fixtures for each affected
  SIT code family.

These remain closure requirements for `CF-0003` as a whole; they do not block
the approved narrow Item 28A or Item 28B interpretations.

Affected discoveries: `DISC-0031`, `DISC-0075`, `DISC-0078`, `DISC-0079`,
`DISC-0086`, `DISC-0087`.

## CF-0004 — Reweigh-tolerance branch input

### Claims and ambiguity

| Claim | Source provenance | Claim | Status |
|---|---|---|---|
| `CLM-0023` | `SRC-DP3-2026-400NG`; publication 2025-12-05; effective 2026-05-15-2027-05-14; Item 4.5(a)-(b), p. 19 | A lower reweigh makes the reweigh fee payable only when the difference is less than 150 lbs for a shipment weighing 5,000 lbs or less, or less than 5 percent of the lower net scale weight for a shipment weighing more than 5,000 lbs. | Reviewed direct text; branch fact disputed |
| `CLM-0028` | Same source/version/effective period; Item 4.13(3)-(5), pp. 22-23 | The completed containerized reweigh can require reimbursement when the new tare exceeds the original tare and the applicable greater-than-150-lb or at-least-5-percent threshold is crossed. | Reviewed direct text; branch fact disputed |
| `CLM-0044` | `SRC-DP3-ADV-23-0004`; published 2022-10-13; effective for pickup dates from 2022-10-24; para. 3.4, p. 1; retrieved 2026-08-07 | USTRANSCOM directs the TSP to invoice on the lesser weight if the reweigh first falls within the tariff tolerance. | Reviewed direct text; confirms sequence but does not identify the branch fact |
| `CLM-0045` | `SRC-DP3-2026-400NG`; publication 2025-12-05; List of Changes, p. 8 | The tariff history records a 2022 change from “net” to “tare,” a correction back to “net,” and a later generic adjustment to reweigh language. | Reviewed direct text; terminology history does not resolve the selector |

Both passages use a shipment-weight boundary without naming the fact that
selects the branch. Candidate inputs include initial net, reweigh net, lower net,
the containerized provisional net, or another accepted shipment weight. The
choice can change a financial eligibility outcome near 5,000 lbs.

A focused authoritative-source pass on 7 August 2026 archived and visually
reviewed Advisories 23-0004 and 22-0097B, inspected the tariff's own change
history, and searched official USTRANSCOM, DTR, CBCA, and GAO material. Advisory
23-0004 is the closest publisher clarification, but its conditional wording
places lesser-weight invoicing after the tolerance decision. Advisory 22-0097B
states that the approved final business-rule documents would be published and
individual comment replies would not be sent. Neither source supplies a worked
5,000-pound boundary example or names the controlling weight fact. The search
record is in `docs/reweigh-tolerance-source-research.md`; the source-only pass
did not resolve `CF-0004`.

Decision 0006's proposed dossier now compares initial net, completed reweigh
net, lower net, containerized provisional net, and a hypothetical reviewed
accepted weight across thirteen exact boundary cases. Initial net is the
provisional lead because it is stable, available before both decisions, and an
explicit Item 4.5 operand; that rationale is an interpretation, not a direct
source claim. The preserved proposal did not itself approve the interpretation.

### Scoped decision

On 7 August 2026, the project owner explicitly selected Decision 0006
Alternative A. `INT-0003` approves final reviewed initial net scale weight as
the branch selector for domestic 400NG Items 4.5 and 4.13 only for actual pickup
dates 2026-05-15 through 2027-05-14. Exactly 5,000 pounds uses the at-or-below
branch. Missing, blocked, conflicting, unreviewed, or constructive-only initial
net cannot be substituted. The accepted decision is preserved in
`docs/decisions/0006-cf-0004-initial-net-scoped.md`.

This resolves the conflict for the approved scope and permits publication of
the two eligibility rules. It does not authorize a fee rate, billing code,
discount treatment, reimbursement/refund amount, charge allocation, live
submission, or money movement. `CF-0001` and `CF-0003` remain separate blockers
to reweigh-fee money.

### Scope reconciliation

This ambiguity does not create a 400NG-versus-Tender conflict over the general
lower-weight obligation. Tender Weighing Shipments 8.a.(2)(c)-(d) requires lower
weight invoicing and later refunds; Item 4.5 governs the separate reweigh-fee
question. The full scope analysis is in
`docs/reweigh-controlling-weight-reconciliation.md`.

### Current behavior

- Use only the `INT-0003` initial-net selector inside the approved 2026 scope.
- Publish eligibility booleans only; do not produce unsupported fee or
  reimbursement amounts.
- Preserve all candidate weight facts as distinct observations with explicit
  units, timestamps, and ticket provenance.
- Block on missing, unreviewed, conflicting, or provenance-invalid inputs.

### Reopening conditions

- Reopen for a later rate cycle.
- Reopen if an applicable amendment, advisory, written publisher clarification,
  worked example, or contrary adjudicative authority is archived.
- Retain regression tests for exactly 5,000 pounds and the strict `< 150`,
  `> 150`, `< 5%`, and `>= 5%` comparisons.

Affected discoveries: `DISC-0032`, `DISC-0039`, `DISC-0041`.
