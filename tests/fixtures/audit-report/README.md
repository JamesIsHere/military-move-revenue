# Synthetic deterministic audit-report fixtures

`audit-report-cases.json` selects synthetic Item 28A audit cases and combines
Item 28A with Item 28B against one shared invoice/payment history. No real
shipment, person, address, account, signature, or government identifier is
present.

The suite covers a closed report, an open decided exception, a downstream data
block, and an upstream expected-charge block. It verifies canonical JSON,
ordered multi-dimension findings, all-or-nothing totals, source/evidence
projection, adapter validation, data-status binding, and report-output tamper
rejection. The two-family cases prove exact aggregate sums and prove that one
blocked family suppresses all aggregate money while preserving decided findings.
