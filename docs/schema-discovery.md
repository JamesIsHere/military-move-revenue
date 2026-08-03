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
  It compares initial and reweigh values against a tolerance band.
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
  Refunds or later reimbursements may require supplemental treatment.

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
