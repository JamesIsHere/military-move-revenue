# Deterministic Audit Report Policy

- Policy ID: `AUDIT-REPORT-ENVELOPE-V1`
- Version: `2026-08-03.1`
- Schema version: `audit-report-envelope.v1`
- Status: Approved internal deterministic presentation policy
- Effective period: 2026-08-03 until superseded
- Scope: Domestic DP3 TSP-to-Government read-only post-audit reports
- Approval basis: Ratified `goal.md` and the project owner's instruction to
  execute the audit-report plan

This policy presents charge-audit results. It does not create a Government
billing rule, change a published rule package, resolve a blocked fact, submit an
invoice, or move money.

## Envelope contract

One report covers one shipment at one audit cutoff. It contains immutable charge
results, deterministic findings, an exact aggregate summary, source and evidence
indexes, and the policy/version that produced the presentation. Charge results
are sorted by stable charge-instance ID. Findings are sorted by stable finding
ID; a decided charge emits billing, quantity, then payment findings, while each
blocked reason emits a separate review finding.

The report is canonical JSON: UTF-8-compatible ASCII escaping, lexicographically
sorted object keys, and no insignificant whitespace. Monetary and quantity
values remain exact decimal strings. Binary floating point is forbidden.

## Charge-adapter boundary

Each adapter has an immutable ID, version, charge family, audit-policy ID,
deterministic evaluator, and result validator. A report request supplies facts
to the adapter; the report layer does not accept an unverified financial
conclusion. The adapter must validate its upstream expected-charge package,
provenance, calculation trace, evidence, comparison arithmetic, and finding
classification before the result enters the envelope.

Only one instance of a charge family may appear in a shipment report version.
Adding a family requires a new registered adapter with its own validator; it
must not broaden an existing adapter's source interpretation.

## Exact aggregation and blockers

For a fully decided report, totals are exact sums of the adapter comparisons:

- billing variance: `invoiced_amount - expected_amount`;
- payment variance: `paid_amount - invoiced_amount`; and
- realized variance: `paid_amount - expected_amount`.

If any adapter is blocked, report status and totals status are `BLOCKED`, no
aggregate monetary values are emitted, and human review is required. This
all-or-nothing rule prevents incomplete coverage from appearing to be a complete
shipment total. Open decided exceptions also require human review but retain
their authoritative charge comparison.

## Explanation, source, and evidence contract

Explanations are rendered from versioned deterministic code templates. They
state the exact compared inputs, variance expression, result, and finding code.
Blocked explanations state only the adapter's reason code and never manufacture
an amount.

The source index preserves three adapter provenance scopes: expected-charge
authority, charge-audit policy, and observed invoice/payment authority. The
evidence index preserves reviewed expected-charge, invoice, and payment evidence
link IDs plus reviewed completeness-assertion IDs. Report-policy provenance is
identified separately. Altered explanations, sources, evidence, findings,
ordering, totals, or adapter metadata invalidate the envelope.

## AI boundary

AI may draft a candidate narrative outside the authoritative envelope. AI does
not select finding codes, calculate money, fill missing evidence, clear blockers,
or author the report's financial conclusions. Only registered deterministic
adapters and the versioned report templates produce authoritative output.
