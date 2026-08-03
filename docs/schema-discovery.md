# Schema Discovery Workbook

## Why this exists

The initial schema will be derived from sources. This workbook records the path
from a source element to a domain concept and eventually to a physical field.

## Extraction sequence

1. Inventory and archive the authoritative source.
2. Identify source elements: form blocks, tariff items, rate columns, EDI
   elements, code tables, and workflow statements.
3. Translate each element into a domain concept without choosing SQL types yet.
4. Record cardinality, unit, temporal behavior, sensitivity, validation, and
   provenance.
5. Reconcile duplicate concepts and contradictions across sources.
6. Draft the conceptual entity model.
7. Draft the logical schema.
8. Select physical types only after interchange constraints and representative
   values are understood.

## Source-to-field template

| Attribute             | Description                                                                      |
|-----------------------|----------------------------------------------------------------------------------|
| Discovery ID          | Stable identifier for this finding                                               |
| Source ID             | Entry from `source-register.md`                                                  |
| Source locator        | Item, section, page, block, segment, or cell range                               |
| Source label          | Original term used by the source                                                 |
| Domain concept        | Normalized business meaning                                                      |
| Candidate field       | Provisional implementation name                                                  |
| Entity                | Candidate owner                                                                  |
| Logical type          | Identifier, text, date, instant, money, quantity, code, boolean, document, event |
| Unit/currency         | Explicit measurement semantics                                                   |
| Cardinality           | One, optional, or repeating                                                      |
| Required when         | Conditional requirement                                                          |
| Validation            | Invariants and cross-field checks                                                |
| Temporal behavior     | Effective-dated, event time, observed time, or timeless                          |
| Sensitivity           | Public, operational, proprietary, PII, sensitive PII, unknown                    |
| Evidence role         | Whether it proves a billable fact                                                |
| Interpretation status | Candidate, reviewed, disputed, approved                                          |
| Notes/open questions  | Unresolved issues                                                                |

## Seed discoveries — DD Form 619

These are provisional until the source artifact is archived and reviewed.

| ID        | Source       | Concept                               |
|-----------|--------------|---------------------------------------|
| DISC-0001 | Block 1      | Bill of lading identifier             |
| DISC-0002 | Block 2a     | Customer identity                     |
| DISC-0003 | Block 2b     | Rank or grade                         |
| DISC-0004 | Blocks 3a/3c | Shipment endpoint                     |
| DISC-0005 | Block 3b     | Pickup date                           |
| DISC-0006 | Block 4      | Ordering activity                     |
| DISC-0007 | Block 5      | TSP                                   |
| DISC-0008 | Block 5a     | TSP shipment reference                |
| DISC-0009 | Blocks 5b–5d | TSP attestation                       |
| DISC-0010 | Blocks 6a–6b | Performing agent                      |
| DISC-0011 | Blocks 7a–7f | Additional service                    |
| DISC-0012 | Block 8      | Service remarks and customer initials |
| DISC-0013 | Block 9a     | Performance location role             |
| DISC-0014 | Blocks 9b–9c | Customer attestation                  |

Schema mappings:

- `DISC-0001` → `shipment.bill_of_lading_number`; identifier; one.
  External identifier; length awaits the interface specification.
- `DISC-0002` → `customer` party record; person; one.
  Contains PII; fixtures require substitution.
- `DISC-0003` → `customer.rank_grade_code`; controlled code; optional.
  Prefer a reference table when the official value set is confirmed.
- `DISC-0004` → `shipment_stop`; location role; two or more.
  Use roles because extra pickups and deliveries can repeat.
- `DISC-0005` → `shipment.pickup_date`; local date; one.
  Candidate rule-package selection fact.
- `DISC-0006` → `organization` plus shipment role; party role; one.
  May require an installation/location relationship.
- `DISC-0007` → `organization` plus TSP role; party role; one.
  SCAC is a separate external identifier.
- `DISC-0008` → `shipment_external_identifier`; identifier; optional.
  Namespace it by the assigning party or system.
- `DISC-0009` → `document_attestation`; signature event; one.
  Store signer role and signed date separately from the image.
- `DISC-0010` → `organization` plus agent role; party role; optional.
  Agent and TSP remain distinct roles even when one organization fills both.
- `DISC-0011` → `service_performance`; repeating event; zero or more.
  Do not create one boolean column per service type.
- `DISC-0012` → `service_evidence_annotation`; text/attestation; repeating.
  Link each annotation to a service when possible.
- `DISC-0013` → `service_performance.stop_role`; controlled code; one per service.
  Values include origin, destination, and other.
- `DISC-0014` → `document_attestation`; signature event; one.
  Signature data may be excluded from the sanitized corpus.

## Reviewed discoveries — TPPS billing workflow

These findings were checked against the archived PDF and rendered pages.

| ID        | Source              | Concept                             |
|-----------|---------------------|-------------------------------------|
| DISC-0015 | A-A-12(d),(j)       | BL-to-invoice relationship          |
| DISC-0016 | A-A-12(c)           | Invoice submission channel          |
| DISC-0017 | A-A-12(d),(f)       | Invoice service line                |
| DISC-0018 | A-A-12(h)           | Billed versus actual weight         |
| DISC-0019 | A-A-12(i)           | Transport/syntax acknowledgement    |
| DISC-0020 | A-A-12(i)           | Downstream business error           |
| DISC-0021 | A-A-12, para. 9     | External line identity              |
| DISC-0022 | A-A-12–15           | Line approval lifecycle             |
| DISC-0023 | A-A-13(c),(d)       | Status reason and response deadline |
| DISC-0024 | A-A-15(e)           | Status semantics                    |
| DISC-0025 | A-A-15(g)           | Quantity correction                 |
| DISC-0026 | A-A-12(g)           | Document retention                  |
| DISC-0027 | A-A-13–15           | Documentation sampling              |
| DISC-0028 | A-A-12(j)           | Linehaul uniqueness and supplements |

Schema mappings:

- `DISC-0015` → `invoice.bill_of_lading_id`; relationship; many invoices to one BL.
  Invoice numbers are unique within a TSP namespace, not necessarily globally.
- `DISC-0016` → `invoice_submission.channel`; controlled code; one per attempt.
  EDI 859 and TPPS Web are channels; model repeated attempts.
- `DISC-0017` → `invoice_line`; financial line; one or more.
  It includes service identity and origin/destination responsibility.
- `DISC-0018` → `invoice_line_weight_basis`; quantity references; conditional.
  Billed weight and actual net/gross weight are separate facts.
- `DISC-0019` → `external_message`; typed event; zero or more.
  EDI 997 represents acknowledgement or syntax rejection.
- `DISC-0020` → `external_message`; typed event; zero or more.
  EDI 824 business errors remain distinct from syntax failures.
- `DISC-0021` → `invoice_line_external_id`; identifier; one after TPPS acceptance.
  LineIDC distinguishes equal item codes with different quantities.
- `DISC-0022` → `invoice_line_status_event`; event; zero or more.
  Preserve Pending, Approved, Denied, In Dispute, and Updated as history.
- `DISC-0023` → `invoice_line_review_event`; note and deadline; conditional.
  Denials and disputes require reasons; requests may have seven-day deadlines.
- `DISC-0024` → `line_status_code`; controlled reference; one per event.
  Approval, denial, and dispute have different performance/quantity meanings.
- `DISC-0025` → `invoice_line_revision`; immutable version; zero or more.
  A disputed quantity may change; approved or denied quantities may not.
- `DISC-0026` → `retention_policy`; duration/policy; one per governing scope.
  Model the six-year policy, not merely a deletion date.
- `DISC-0027` → `evidence_review`; review event; zero or more.
  Sampling records the invoice/BL, requested documents, and action.
- `DISC-0028` → invoice-line relationship rule; constraint; conditional.
  Linehaul occurs once per BL; supplemental linehaul uses LHSADD.

## Reviewed discoveries — 400NG Item 4, weights and reweighs

| ID        | Source          | Concept                               |
|-----------|-----------------|---------------------------------------|
| DISC-0029 | Item 4.1        | Shipment weighing                     |
| DISC-0030 | Items 4.2–4.4   | Reweigh kind and authorization        |
| DISC-0031 | Item 4.4        | Tariff item versus billed item code   |
| DISC-0032 | Item 4.5        | Reweigh-fee eligibility               |
| DISC-0033 | Item 4.8        | Automatic-reweigh threshold           |
| DISC-0034 | Item 4.9        | Weight derivation method              |
| DISC-0035 | Item 4.9(h),(i) | Special article weight                |
| DISC-0036 | Item 4.10       | Weight-ticket evidence                |
| DISC-0037 | Item 4.10(b)    | Ticket-to-measurement cardinality     |
| DISC-0038 | Item 4.10(d)    | Charge-evidence requirement           |
| DISC-0039 | Items 4.11–4.13 | Controlling billed weight             |
| DISC-0040 | Items 4.11–4.13 | Billing hold and prerequisite         |
| DISC-0041 | Items 4.12–4.13 | Refund or reimbursement               |

Schema mappings:

- `DISC-0029` → `weighing_event`; event; two or more observations.
  Gross, tare, and derived net retain sequence and context.
- `DISC-0030` → `reweigh_request`; event/code; zero or more.
  Requested and automatic reweighs have different preapproval behavior.
- `DISC-0031` → `service_definition` plus `billing_item_code`; conditional.
  The rule is Item 4A/4B, but billing uses 226A and a required note.
- `DISC-0032` → `rule_decision`; explained boolean; one per candidate fee.
  It compares initial and reweigh values against a tolerance band. The weight
  fact selecting the 5,000-lb tolerance branch is disputed under `CF-0004` and
  cannot be inferred.
- `DISC-0033` → `rule_decision`; eligibility; conditional.
  The threshold depends on rank/grade category and shipment weight.
- `DISC-0034` → `weight_method_code`; controlled code; one per result.
  Scale difference, manufacturer weight, and constructive weight are distinct.
- `DISC-0035` → `shipment_article_weight`; quantity/method; zero or more.
  PBP&E and gun safes may use different constructive factors.
- `DISC-0036` → `weight_ticket`; document/evidence; one or more.
  It records scale, date, entry type, vehicle, shipper, BL, and signature.
- `DISC-0037` → join relationship; one ticket to one or more measurements.
  One ticket may contain both initial weighings; a reweigh uses another scale.
- `DISC-0038` → `evidence_requirement`; rule; conditional.
  Weight-dependent charges require all determining tickets.
- `DISC-0039` → `weight_determination`; decision; one per rating context.
  The controlling value can change and may combine new gross with original tare.
- `DISC-0040` → `billing_eligibility_decision`; workflow decision; conditional.
  Some delivery charges wait for updated reweigh facts and tickets.
- `DISC-0041` → `invoice_adjustment_line`; signed correction; zero or more.
  Refunds or later reimbursements may require supplemental treatment. The
  containerized reimbursement tolerance shares the `CF-0004` branch-input gate.

## Reviewed discoveries — Tender of Service evidence

| ID        | Source      | Concept                           |
|-----------|-------------|-----------------------------------|
| DISC-0042 | ToS C.12(a) | Accessorial performance evidence  |
| DISC-0043 | ToS C.12(b) | Third-party service cost evidence |
| DISC-0044 | ToS C.12(c) | Service preapproval               |
| DISC-0045 | ToS C.14    | Responsible paying office         |

Schema mappings:

- `DISC-0042` → `service_performance_evidence`; document link; conditional.
  DD 619/619-1 and the customer signature support service performance.
- `DISC-0043` → `third_party_invoice`; financial evidence; conditional.
  It must be paid and support the type of service performed.
- `DISC-0044` → `service_approval_event`; event; conditional.
  The service is requested and preapproved before performance.
- `DISC-0045` → shipment party role; organization role; one.
  Do not store the responsible office only as invoice text.

## Reviewed discoveries — DTR Chapter A-413, government bill of lading

| ID        | Source           | Concept                            |
|-----------|------------------|------------------------------------|
| DISC-0046 | A-413 Blk. 2     | TSP SCAC                           |
| DISC-0047 | A-413 Blk. 4     | Shipment sequence in customer move |
| DISC-0048 | A-413 Blk. 6–8   | Pack, pickup, and delivery dates   |
| DISC-0049 | A-413 Blk. 10    | Customer and entitlement context   |
| DISC-0050 | A-413 Blk. 11    | Shipment authority                 |
| DISC-0051 | A-413 Blk. 13    | Extra pickup or delivery           |
| DISC-0052 | A-413 Blk. 15    | Transportation Control Number      |
| DISC-0053 | A-413 Blk. 17–20 | Shipment parties and locations     |
| DISC-0054 | A-413 Blk. 21    | Bill-charges-to office             |
| DISC-0055 | A-413 Blk. 24    | Appropriation and accounting data  |

Schema mappings:

- `DISC-0046` → `organization_external_identifier`; fixed code; one per initial TSP.
  The source specifies four positions; preserve leading characters.
- `DISC-0047` → `shipment_group_membership.sequence` plus `total`; one.
  Split representations such as “1 of 3” into positive integers.
- `DISC-0048` → `shipment_date_commitment`; local date/type; repeating by type.
  Requested pickup, actual/scheduled pickup, and RDD are distinct facts.
- `DISC-0049` → person and entitlement records; sensitive facts; conditional.
  Name, rank, status, dependency, and authorization facts have different uses.
- `DISC-0050` → `shipment_authority`; structured reference; one or more.
  Separate order number, paragraph, and issuing agency.
- `DISC-0051` → `shipment_stop`; location role; zero or more.
  Stops are not limited to one origin and one destination.
- `DISC-0052` → `shipment_external_identifier`; structured identifier; conditional.
  Preserve the raw TCN and its meaningful parsed positions.
- `DISC-0053` → party and location roles; one or more.
  Keep addresses, installations, agents, facilities, and office codes distinct.
- `DISC-0054` → `billing_party_role`; organization role; one.
  Preserve the selected paying office and the source that determined it.
- `DISC-0055` → `funding_reference`; sensitive structured reference; one or more.
  Preserve raw and typed components; exclude live values from fixtures.

## Reviewed discoveries — DTR Chapter A-402, shipment lifecycle and SIT

All findings in this section use `SRC-DTR-IV-A402`, publication/version 14 July
2026, effective period not stated, retrieved 2026-08-03. The cited pages were
checked against the archived PDF and rendered page images. Interpretation status
is reviewed unless a note identifies a remaining question.

| ID        | Source             | Concept                                  |
|-----------|--------------------|------------------------------------------|
| DISC-0056 | C.3.h, pp. 7–8     | Shipment-date chronology and RDD         |
| DISC-0057 | C.7, pp. 9–10      | Pre-move survey observations             |
| DISC-0058 | D.2, p. 15         | Shipment arrival observation             |
| DISC-0059 | D.3, pp. 15–16    | Delivery request, schedule, and event     |
| DISC-0060 | D.4, p. 16         | Partial-delivery portion                 |
| DISC-0061 | C.9; D.5(a), pp. 10–17 | SIT episode and rating locality    |
| DISC-0062 | C.9; D.5; F.5, pp. 10–19, 28–29 | SIT authorization workflow |
| DISC-0063 | D.5(a)(2–3), p. 17 | SIT control identifier and register      |
| DISC-0064 | C.9(b); D.5(a)(3), pp. 10, 17–18 | SIT period dates and expiration |
| DISC-0065 | D.5(a)(3); F.6, pp. 18, 29 | SIT extension request and decision |
| DISC-0066 | C.9(c), p. 11      | Origin-SIT release and entitlement balance |
| DISC-0067 | D.5(b)(2), p. 18  | Destination-SIT effective date           |
| DISC-0068 | D.5(b)(4); F.5(a)(6), pp. 18, 29 | Split-shipment SIT        |
| DISC-0069 | D.5(c); F.7, pp. 19, 29–30 | SIT conversion and liability end |
| DISC-0070 | F.8(c), pp. 30–31 | Weight-entry operational prerequisites  |
| DISC-0071 | D.1–3; F.8(d), pp. 15–16, 31 | Status and record-change history |

Schema mappings:

- `DISC-0056` → `shipment_date_commitment` plus `rule_decision`; typed local-date
  observations; repeating by role and source. Preserve counseling desired dates,
  booking preferred dates, pre-move agreed dates, calculated RDD, and actual
  pickup/delivery dates instead of overwriting one value. The basic RDD rule is
  pickup date plus transit time, subject to an agreed earlier DDD and scheduling
  exceptions.
- `DISC-0057` → `pre_move_survey` plus extracted observations; event/document;
  one or more attempts and one completed survey per applicable shipment. Record
  method, estimated weight, agreed pack/pickup dates, delivery-date information,
  special handling needs, completion timing, and customer-unavailability reason.
- `DISC-0058` → `shipment_arrival_event`; event; one or more when a shipment is
  split. Record arrival date, whole/split indicator, observed shipment weight,
  requested/actual delivery dates, and attempted-delivery date as separately
  typed facts.
- `DISC-0059` → `delivery_request`, `delivery_schedule_event`, and
  `delivery_event`; repeating events. Preserve requester, communication channel,
  requested date/address, TSP-confirmed schedule, schedule changes, actual date,
  and entry timestamp. Addresses and customer contact data require sanitization.
- `DISC-0060` → `shipment_portion` plus `partial_delivery_event`; zero or more.
  Link requested inventory item identifiers, delivery address, requested and
  actual dates, weight removed, weight remaining in SIT, and the residual stored
  portion without treating the entire shipment as delivered.
- `DISC-0061` → `sit_episode`; zero or more per shipment or shipment portion.
  Record origin/destination/intermediate scope, reason, approved facility,
  storage location, and the destination city/installation used for charges.
  A servicing-PPSO exception to the BL Block 18 locality must be preserved as an
  authorization, not as an unexplained replacement value.
- `DISC-0062` → `sit_authorization_event`; request/decision history; one or more
  per episode. Store requester, PPSO decision, status, reason, decision time, and
  notification references. Every placement in SIT requires approval through
  DPS; approval generates the control identifier.
- `DISC-0063` → `sit_control_identifier`; namespaced structured identifier; one
  per approved episode or split portion. Preserve the raw nine-digit string
  and parsed two-digit year, three-digit Julian day, and four-digit daily
  sequence. Do not infer a full century without contextual evidence.
- `DISC-0064` → `sit_date_event`; typed local dates; repeating by role. Roles
  include placed/ordered in, ordered out, release, expiration, and entitlement
  end. Store the stated expiration separately from calculated or extended dates.
- `DISC-0065` → `sit_extension_request` plus `sit_extension_decision`; zero or
  more. Link the DD Form 1857 evidence, request date, PPSO approval/denial,
  projected termination date, new expiration date, and notification events.
- `DISC-0066` → `sit_release_event` plus `sit_entitlement_balance_decision`;
  conditional. Origin release requires the SF 1200, a new RDD, and inclusive-day
  math: days used equals release date minus placed-in-storage date plus one; the
  destination balance equals authorized days minus used days.
- `DISC-0067` → `sit_authorization_effective_date`; explained rule outcome;
  conditional. For the cited no-direct-delivery scenario, approved destination
  SIT begins on the offer-for-delivery date rather than arrival date unless both
  occur on the same day.
- `DISC-0068` → `shipment_portion` plus portion-level `sit_episode`; one or more
  for split shipments. Each stored portion requires its own control identifier
  and weight-ticket evidence. Minimum-weight and employee partial-delivery rules
  remain subject to reconciliation with 400NG and entitlement sources.
- `DISC-0069` → `sit_conversion_event`; zero or one Government-to-customer
  conversion per episode. Preserve the customer-contact prerequisite, notice,
  non-retroactive effective time, payer-responsibility change, TSP-liability end,
  warehouse final-destination role, and remaining Government-paid delivery-out
  entitlement.
- `DISC-0070` → `operational_eligibility_decision`; explained system gate;
  conditional. DPS weight entry gates invoicing, in-transit updates, arrival,
  destination-SIT requests, and delivery scheduling. Keep this operational gate
  distinct from legal charge eligibility.
- `DISC-0071` → `shipment_status_event` plus `record_change_event`; repeating
  event histories. Store status code, en-route location note, ETA, RDD, delivery
  date, DTS entry/receipt dates, actor, and recorded time. Weight entry triggers
  the DPS `IT` status and actual delivery triggers `Delivered Complete`; neither
  should erase preceding states or observations.

## Reviewed discoveries — 400NG SIT eligibility and rating

All findings in this section use `SRC-DP3-2026-400NG`, publication/version 5
December 2025, effective 15 May 2026 through 14 May 2027, retrieved 2026-08-03.
The cited pages were checked against the archived PDF and rendered page images.
Interpretation status is reviewed unless a note identifies a conflict.

| ID        | Source                         | Concept                                  |
|-----------|--------------------------------|------------------------------------------|
| DISC-0072 | Item 17.2–5, p. 27; Item 185.2, p. 57 | SIT rating locality and billing trigger |
| DISC-0073 | Item 17.3, p. 27               | Aggregate authorized SIT period          |
| DISC-0074 | Item 17.7, p. 27; Item 185.3, p. 57 | SIT accrual interval and cessation |
| DISC-0075 | Item 17.9, p. 28; Item 210.2(c), p. 59 | Split and partial-delivery weight basis |
| DISC-0076 | Item 17.12–13, p. 29            | SIT custody and partial-withdrawal evidence |
| DISC-0077 | Item 17-1.2–4, pp. 30–31       | Attempted-delivery eligibility evidence  |
| DISC-0078 | Item 185, p. 57; Appendix A, pp. 83–84 | SIT storage calculation             |
| DISC-0079 | Item 210.1–2, pp. 58–59; Appendix A, p. 84 | SIT pickup/delivery calculation |
| DISC-0080 | Item 1.2(b–c), p. 18; Item 17.2(b), p. 27; Item 210.2(e), p. 59 | SIT effective-date selection |
| DISC-0081 | Item 17-2.2–8, pp. 31–32       | Post-conversion payer and delivery-out rating |

Schema mappings:

- `DISC-0072` → `sit_rating_context` plus `billing_eligibility_decision`;
  explained selection; one per candidate SIT charge. Preserve the requested
  pickup/delivery address and ZIP3 from BL Block 19 or 18 as accepted by the TSP,
  the origin/destination SIT role, actual warehouse location, and billing-trigger
  event. The rating locality is the accepted BL address, not the SIT facility.
- `DISC-0073` → `sit_entitlement_period` plus authorization history; quantity in
  calendar days; one current explained decision with prior versions preserved.
  One or more SIT episodes share a 90-day aggregate ceiling unless an authorized
  Government representative grants additional storage. External entitlement
  sources may further constrain the authorized amount and remain to be reconciled.
- `DISC-0074` → `sit_charge_interval`; inclusive local-date interval; one or more
  per episode. Item 185 counts both the placed-in and removed-from days. If TSP
  commitments delay removal, accrual stops no later than the fifth Government
  business day after the requested delivery date, or on the earlier removal day.
  Preserve requested delivery, placed-in, removed-from, and calculated cessation
  dates plus the Government-business-day calendar version used.
- `DISC-0075` → `sit_weight_basis_decision`; explained quantity; one per storage
  or pickup/delivery charge. Overflow portions stored on different dates are
  rated separately, but the 1,000-lb storage minimum applies to their combined
  stored weight and later charges use combined weight. A portion delivered out
  of SIT uses actual net weight without a minimum; below 1,000 lbs it is billed
  temporarily as Item 226A with detailed notes. Portion and remainder weights
  must therefore remain distinct observations.
- `DISC-0076` → `sit_custody_record`, `partial_delivery_request`, and evidence
  links; repeating. Preserve the BL-linked inventory, origin/destination,
  article condition at receipt/release, charge/payment dates, storage movement
  dates, ordered inventory item numbers, labor approval, actual withdrawn
  weight, and continuing stored weight. These records support both custody and
  charge eligibility.
- `DISC-0077` → `attempted_delivery_event` plus `billing_eligibility_decision`;
  conditional event and evidence bundle. Required facts include PPSO scheduling
  or confirmation of customer fault, timely DPS scheduled-delivery entry,
  contact with PPSO while at the residence, requested preapproval, and the
  one-hour free-wait interval. An attempted-delivery charge is not inferred from
  a failed delivery event alone.
- `DISC-0078` → `rate_table`, `rate_cell`, and `charge_calculation`; money per
  hundredweight and day. Item 185A equals first-day rate × cwt × inverse SIT
  discount; Item 185B equals additional-day rate × cwt × additional days ×
  inverse SIT discount. The Appendix A page 84 subheading says `185E` while the
  governing item and calculation text say `185B`; preserve both claims as a
  source-label conflict and require interpretation approval before implementation.
- `DISC-0079` → `sit_pickup_delivery_band` plus `charge_calculation`; distance in
  miles and exact money. Up to 30 miles uses 210A. Over 30 through 50 miles adds
  210A and 210B but invoices only the combined total as 210B. Over 50 miles uses
  linehaul computation under 210C, or 210F for Alaska. Record the BL-address
  anchor, actual residence, mileage source/version, service-area schedule,
  portion weight, dSIT, approvals, and billed item code. Delivery over 100 miles,
  specified amended-order cases, and overtime codes have additional approvals.
- `DISC-0080` → `rule_effective_date_decision`; explained date selection; one per
  rate family. The accepted shipment's original requested pickup date selects
  the TSP SIT discount and the over-50-mile transportation rates/discounts;
  actual pickup date selects the applicable SIT and accessorial tables. Preserve
  both dates and the reason each was selected.
- `DISC-0081` → `sit_conversion_event`, `payer_responsibility_period`,
  `delivery_out_authorization`, and `invoice_adjustment_line`; conditional.
  Government SIT liability ends at midnight on the notified termination day and
  Government pays through that day. Later delivery-out may remain Government
  funded after customer storage balances are paid; it uses current 400NG charges
  less 25 percent based on delivery date, with Item 210C linehaul treatment when
  applicable. Required refunds use Item 226A and a detailed explanation.

## Workbook discoveries — rate, item-code, transit, and mileage structures

These findings were extracted on 2026-08-03 with the user-authorized openpyxl
3.1.5 read-only fallback. Raw hashes were verified against the manifest; ZIP
members were read in memory; formulas were captured but not recalculated. The
structured extract and exact member hashes are in
`sources/derived/2026/workbook-structure.json`. Interpretation status varies by
source as noted below.

| ID        | Source and locator | Concept |
|-----------|--------------------|---------|
| DISC-0082 | `SRC-DP3-2026-RATES`, 2026, effective 2026-05-15–2027-05-14, `Base Point City!A1:E786` | BPC, ZIP3, and service-area assignment |
| DISC-0083 | `SRC-DP3-2026-RATES`, `Geographical Schedule!A1:H229` | Service-area rate profile |
| DISC-0084 | `SRC-DP3-2026-RATES`, `Linehaul!B2:CU91`, `Additional Rates!A2:F71`, `Accessorials!C2:CU101` | Rate matrix dimensions and cells |
| DISC-0085 | `SRC-DP3-2026-RATES`, rate-sheet row 1; `SRC-DP3-2026-400NG`, Item 1.2(c), p. 18 | Rate-table effective-date conflict |
| DISC-0086 | `SRC-DP3-ITEM-CODES`, version 2022-08-12, effective period unresolved, `DOM_400NG!A4:Q149`, legends `A151:L166` | Domestic billing-item-code vocabulary |
| DISC-0087 | `SRC-DP3-ITEM-CODES`, `DOM_400NG!A123:Q144` | SIT billing-code requirements |
| DISC-0088 | `SRC-DP3-2026-TRANSIT`, publication 2025-12-08, effective 2026-05-15, `Appendix L-Domestic!A1:F33` | Domestic transit-time matrix |
| DISC-0089 | `SRC-DP3-MILEAGE-SIT`, version/effective period unstated, `MAIN!C2:H13`, `WORK!A1:I5`, `TREF!A1:C909`, `EREF!A2:B5`, sheets `A:D` | Mileage lookup structure |
| DISC-0090 | `SRC-DP3-MILEAGE-SIT`, `MAIN!G9:H10`, `WORK!G5:I5`, `TT!A1:F21` | Provisional authorized-SIT-day derivation |
| DISC-0091 | `SRC-DP3-MILEAGE-SIT`, `TT!A5:E5`; `SRC-DP3-2026-TRANSIT`, `Appendix L-Domestic!A5:E5` | Transit-table version conflict |

Schema mappings:

- `DISC-0082` → `postal_prefix_assignment`; versioned reference relationship;
  one or more ZIP3 values per BPC and service area. Store ZIP3, BPC, state,
  county, service-area identifier, source version, and effective interval.
  Two-digit source values require left-zero padding and must remain identifiers.
  Interpretation status: reviewed.
- `DISC-0083` → `service_area_rate_profile`; one row per source-version/service
  area. Dimensions include service-area identifier/name, service schedule, SIT
  pickup/delivery schedule, and source version. Measures include linehaul factor,
  Item 135A/B per cwt, Item 185A per cwt, and Item 185B per cwt/day. Store rates
  as exact decimals with explicit units. Interpretation status: reviewed.
- `DISC-0084` → `rate_table`, `rate_dimension`, `rate_band`, and `rate_cell`;
  immutable by source version. Preserve inclusive lower/upper weight in pounds,
  lower/upper distance in miles when applicable, item code, schedule, amount,
  unit, and cell locator. Items 210A/210D are weight-by-schedule matrices while
  210B/210E are schedule scalars. Interpretation status: reviewed.
- `DISC-0085` → two `source_claim` records plus an unresolved
  `interpretation_case`. The workbook labels all rate sheets “Based on Original
  Requested Pickup Date,” while the tariff expressly selects actual-pickup-date
  tables for SIT and listed accessorial services. Do not approve a date-selection
  rule from either label without resolving scope and precedence. Interpretation
  status: disputed.
- `DISC-0086` → `billing_item_code_version` and versioned controlled-value
  relationships. Preserve requested/actual date-basis code, service code, fuel
  treatment, discount family, location role, description, primary/secondary
  units, rate-basing references, required location pairs and N101 codes, L713
  requirement, notes, approval screen, and approval flag. Interpretation status:
  candidate because supersession and continuing applicability are unresolved.
- `DISC-0087` → SIT-specific `billing_item_requirement` records. Item 185A uses
  billed weight and requires the DPS SIT control number in N9; Item 185B uses
  days and billed weight; Items 210A–210F require miles, location pairs, and
  measurement/billed-weight observations; Item 226A requires performed-service
  text. Origin and destination rows are separate code applications, not duplicate
  records. Interpretation status: candidate pending a current item-code version.
- `DISC-0088` → `transit_time_table`, two `rate_band`-like dimensions, and a day
  measure. Select by inclusive mileage band and shipment-weight band; retain the
  Alaska 5-day/16-day adjustment rules as separate conditions. Units are miles,
  pounds, and calendar days. Interpretation status: reviewed for domestic use.
- `DISC-0089` → `mileage_reference_version`, `postal_prefix_assignment`, and
  `distance_lookup`. Inputs are origin/destination ZIP3; TREF selects table codes
  and a compressed matrix; the selected matrix returns miles. Same-BPC results
  require DTOD rather than a workbook mileage. Record raw ZIP3, mapped codes,
  lookup branch, result, and cell provenance. Interpretation status: candidate
  because the tool version/effective period is unstated.
- `DISC-0090` → `sit_entitlement_balance_decision`; provisional formula outcome.
  For the tool's stated non-Alaska direct-delivery scope, mileage is rounded up
  to a 250-mile bracket, weight selects one of five bands, transit days come from
  hidden `TT`, and displayed authorized SIT day equals Excel
  `ROUND(transit_days × 0.7, 0)`. This expression is not approved for financial
  or entitlement execution while its inputs conflict with the current table.
- `DISC-0091` → conflicting versioned `source_claim` records. At 873 miles and
  6,000 lbs, the mileage tool's bracket cell gives 9 transit days while the 2026
  domestic table gives 18. The tool lacks an effective date, so it must not be
  treated as the current transit authority or used to derive SIT entitlement
  until reviewed. Interpretation status: disputed.

## Candidate domain areas

The current sources suggest, but do not yet ratify, these entity families:

- Source, source version, source locator, and interpretation.
- Program and rule package.
- Rule, condition, calculation, evidence requirement, and rule outcome.
- Rate table, rate dimension, and rate cell.
- Organization, person, external identifier, and shipment party role.
- Shipment, shipment stop, shipment date/event, and service code.
- Weight observation, scale/ticket evidence, and controlling-weight decision.
- Service performance and approval.
- SIT episode and storage facility.
- Document, document version, extracted fact, and attestation.
- Bill of lading, invoice, invoice version, invoice line, and adjustment.
- Submission attempt, acknowledgement, business error, and line decision.
- Payment, payment allocation, reconciliation, and audit finding.
- Human review case and interpretation decision.

## Questions that must remain open

- Which date controls each rule and rate family when sources use different dates?
- Which weight observation controls each charge after a reweigh?
- Which service items may repeat on one invoice or across supplemental invoices?
- How are DPS item codes versioned and retired?
- Which location representation controls mileage and rate lookup?
- What exact EDI element constraints must be preserved at integration boundaries?
- Which facts are recorded as stated, observed, approved, billed, or paid values?
- Which entitlement and tariff rules set the initial authorized SIT duration for
  each in-scope domestic shipment, and which date legally begins each charge?
- How must delivery offers and unsuccessful customer-contact attempts be
  evidenced before destination SIT is billable?
- How do 400NG minimum-weight rules apply to each portion of a split shipment,
  especially where Chapter A-402 distinguishes employees from other customers?
- Does the Appendix A `185E` label on page 84 merely contain a typographical
  error, given that Item 185 and the adjacent formula identify `185B`?
- Does the baseline workbook's original-requested-pickup-date banner apply to
  SIT/accessorial tabs despite the explicit actual-pickup-date exception in
  400NG Item 1.2(c)?
- What publication/effective date governs the mileage/transit/SIT tool, and why
  does its hidden domestic transit table differ from the 2026 transit workbook?
- Has the 12 August 2022 domestic item-code listing been superseded, or is its
  controlled vocabulary still authoritative for 2026 shipments?
