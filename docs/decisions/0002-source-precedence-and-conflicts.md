# Decision 0002 — Source Precedence and Conflict Handling

- Status: Accepted
- Date: 2026-08-03

## Context

Domestic DP3 post-audit uses sources that perform different legal and operational
jobs. The 400NG tariff states charge rules, rate workbooks supply numeric cells,
DTR and Tender sources establish operational duties and authorizations, and
item-code or EDI references define system representations. A flat ranking would
allow a code list to create entitlement or a workbook banner to silently override
a specific tariff rule.

The archived sources already contain material disagreements about the date that
selects SIT/accessorial tables and the current domestic transit-time values.
Those disagreements must remain reproducible and reviewable.

## Decision

### 1. Applicability comes before precedence

A source claim is considered only after matching:

- program and service scope;
- billing relationship;
- shipment geography and code of service;
- legally relevant event date;
- source effective period and supersession status; and
- the business question being answered.

Retrieval date does not establish legal effect. “Current at retrieval” is not a
substitute for a publication version or effective period.

### 2. Precedence is specific to the question

| Question | Primary controlling source | Permitted supporting source |
|---|---|---|
| Charge eligibility, minimums, date selection, and calculation method | Applicable 400NG tariff, amendment, or incorporated controlling advisory | Tender/DTR for required operational facts; adjudicative authority for interpretation |
| Numeric rate, rate band, and geographic schedule | Applicable rate package incorporated by 400NG | Tariff for selection method, scope, units, and adjustments |
| Operational authorization, status, and performance obligation | Applicable DTR chapter, Tender of Service, or controlling program direction | Tariff where billing expressly depends on the event |
| Billing item code, EDI field, unit, location qualifier, or approval screen | Applicable DTEB/TPPS specification or official item-code version | Tariff/Tender/DTR for the underlying entitlement and evidence |
| Evidence required to support a charge | Applicable tariff, Tender, DTR, and TPPS rule for that evidence role | Official forms and system guidance for representation |
| Disputed interpretation | All applicable governing sources, then relevant adjudicative decisions | Official training and contextual material only as noncontrolling explanation |

An operational or representation source cannot independently create a financial
entitlement. A rate workbook supplies values only within the rule and effective
date selected by the controlling governing text.

### 3. Version and specificity rules

Within the same authority and question:

1. An applicable amendment or explicit superseding direction controls an older
   version for its effective period.
2. A provision expressly scoped to the charge or event controls a general
   statement in the same package.
3. An incorporated source controls only the function delegated to it. Numeric
   incorporation does not delegate eligibility or date selection unless the
   governing text says so.
4. A later retrieval does not supersede an earlier publication.
5. A source with unresolved effective or supersession metadata may inform a
   provisional schema but cannot publish a rule package or controlled-value set.

### 4. Conflict records are append-only

Every materially distinct claim is preserved with:

- claim ID and normalized question;
- source ID, version/publication, effective period, locator, and retrieval date;
- authority class and delegated source function;
- extracted claim or faithful paraphrase;
- extraction method and interpretation status; and
- affected discoveries, rules, rate tables, tests, and outputs.

Corrections add a new source version, claim, or interpretation decision. They do
not rewrite the historical claim.

### 5. Conflict workflow

1. Detect competing claims or a missing version/effective period.
2. Classify the case as direct, scope, version, numeric, label/typographical,
   legal-versus-operational, or currency gap.
3. Verify each claim against the archived authoritative artifact.
4. Search applicable amendments, advisories, incorporated sources, and
   adjudicative authority before deciding.
5. Record the provisional precedence analysis and exact remaining evidence.
6. For a material unresolved case, stop the affected deterministic decision and
   emit a human-review result. Unaffected fields and rules may continue.
7. Approve an interpretation only with reviewer identity/role, decision date,
   rationale, effective scope, cited claims, and required regression tests.
8. Reopen the case when a new applicable source version or contrary claim is
   registered.

### 6. Interpretation statuses

- `candidate`: extracted but not sufficiently verified or versioned.
- `reviewed`: checked against the archived source; not necessarily approved for
  implementation.
- `disputed`: competes with another applicable claim or lacks material version
  authority.
- `approved`: a scoped interpretation decision authorizes implementation.
- `superseded`: retained historically but replaced for a later effective scope.

Only `approved` material interpretations may enter a published rule package.

## Consequences

- The system needs source-claim, conflict-case, and interpretation-decision
  records in addition to source documents and locators.
- A calculation result can identify an unresolved interpretation instead of
  producing a false definitive amount.
- Rate and rule packages remain immutable; later corrections create versions.
- Current conflicts are registered in `docs/conflict-register.md` and remain open
  until their required evidence and approval are present.
