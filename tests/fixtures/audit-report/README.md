# Synthetic deterministic audit-report fixtures

`audit-report-cases.json` selects synthetic Item 28A audit cases from the
existing rating and immutable invoice/payment fixtures. No real shipment,
person, address, account, signature, or government identifier is present.

The suite covers a closed report, an open decided exception, a downstream data
block, and an upstream expected-charge block. It verifies canonical JSON,
ordered multi-dimension findings, all-or-nothing totals, source/evidence
projection, adapter validation, data-status binding, and report-output tamper
rejection.
