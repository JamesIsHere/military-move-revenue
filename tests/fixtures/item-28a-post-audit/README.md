# Synthetic Item 28A post-audit fixtures

`item-28a-audit-cases.json` combines two synthetic logical fixtures: the
published Item 28A rating facts and an immutable corrected invoice/payment
history. No real shipment, invoice, payment, person, address, account, signature,
or government identifier is present.

Absence is classified as missing or unpaid only when reviewed completeness
assertions cover invoice and payment history through the audit cutoff. The suite
also covers current-version selection, exact variances, unsupported charges,
quantity mismatch, ambiguous matching, evidence blocks, malformed histories,
and result tampering.
