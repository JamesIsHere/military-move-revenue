# Provisional Conceptual Schema

> Status: provisional. Derived from the first reviewed 400NG, Tender of Service,
> and TPPS pages. Rate-workbook and EDI element inspection are still pending.

## Model shape

```mermaid
erDiagram
    SOURCE_DOCUMENT ||--o{ SOURCE_VERSION : publishes
    SOURCE_VERSION ||--o{ SOURCE_LOCATOR : contains
    SOURCE_LOCATOR ||--o{ RULE : supports
    RULE_PACKAGE ||--o{ RULE : groups
    RULE_PACKAGE ||--o{ RATE_TABLE : selects

    SHIPMENT ||--o{ SHIPMENT_PARTY_ROLE : assigns
    ORGANIZATION ||--o{ SHIPMENT_PARTY_ROLE : fulfills
    PERSON ||--o{ SHIPMENT_PARTY_ROLE : fulfills
    SHIPMENT ||--o{ SHIPMENT_STOP : visits
    SHIPMENT ||--o{ SHIPMENT_EVENT : records
    SHIPMENT ||--o{ BILL_OF_LADING : documented_by

    SHIPMENT ||--o{ WEIGHING_EVENT : weighed_by
    WEIGHT_TICKET ||--o{ WEIGHT_TICKET_MEASUREMENT : contains
    WEIGHING_EVENT ||--o{ WEIGHT_TICKET_MEASUREMENT : evidenced_by
    SHIPMENT ||--o{ WEIGHT_DETERMINATION : controls

    SHIPMENT ||--o{ SERVICE_PERFORMANCE : receives
    SERVICE_DEFINITION ||--o{ SERVICE_PERFORMANCE : classifies
    SERVICE_PERFORMANCE ||--o{ SERVICE_APPROVAL_EVENT : reviewed_by
    SERVICE_PERFORMANCE ||--o{ EVIDENCE_LINK : supported_by
    DOCUMENT ||--o{ EVIDENCE_LINK : proves

    BILL_OF_LADING ||--o{ INVOICE : billed_through
    INVOICE ||--|{ INVOICE_LINE : contains
    SERVICE_DEFINITION ||--o{ INVOICE_LINE : billed_as
    INVOICE_LINE ||--o{ INVOICE_LINE_VERSION : revised_as
    INVOICE_LINE ||--o{ INVOICE_LINE_STATUS_EVENT : transitions
    INVOICE ||--o{ INVOICE_SUBMISSION : submitted_by
    INVOICE_SUBMISSION ||--o{ EXTERNAL_MESSAGE : acknowledged_by

    INVOICE_LINE ||--o{ PAYMENT_ALLOCATION : settled_by
    PAYMENT ||--o{ PAYMENT_ALLOCATION : allocates
    INVOICE_LINE ||--o{ AUDIT_FINDING : evaluated_by
    RULE ||--o{ RULE_DECISION : executes
    INVOICE_LINE ||--o{ RULE_DECISION : explained_by
```

## Key modeling conclusions

### Facts are observations, not mutable shipment columns

Weights, approvals, statuses, submissions, and payments can occur repeatedly and
can contradict earlier observations. Store each event and derive the current or
controlling value through an explicit decision.

### Performance, authorization, and billing are distinct

A service can be requested, preapproved, performed, documented, billed, disputed,
and paid. Those are different events. A single `services` row with boolean flags
would erase order, actors, reasons, and evidence.

### External vocabularies remain versioned boundaries

400NG item numbers, DPS/TPPS billing item codes, EDI identifiers, SCACs, and
government office codes should be versioned reference records. Internal entities
may reference them but should not use the external code as the database primary
key.

### Financial records are append-only

An invoice may have multiple submissions and a BL may have multiple invoices.
Disputed quantities can be revised, while approved or denied lines have different
constraints. Preserve versions and adjustments instead of updating the original
line in place.

### Evidence proves a claim, not merely a shipment

Documents should link to the exact fact, service, invoice line, or approval they
support. This permits an audit finding to distinguish missing evidence from an
ineligible or incorrectly calculated charge.

## Physical types intentionally deferred

Identifiers will remain logical identifiers until DTEB/TPPS length and character
constraints are inspected. Money will use exact decimal semantics; weights and
other quantities will carry explicit units. Dates, local times, and instants will
not be collapsed into strings.
