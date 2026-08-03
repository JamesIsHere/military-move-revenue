# Fixtures

This directory will contain synthetic boundary cases during initial development.
Authorized sanitized historical cases must remain distinguishable from synthetic
fixtures and may require a separate access-controlled location.

No fixture may contain live personal, financial, government, shipment, or employer
identifiers.

## Logical-schema scenarios

`logical-schema/` contains explicitly synthetic JSON scenarios for the draft
logical contract. Decimal money and quantity values are JSON strings so loading a
fixture cannot first pass them through binary floating point. Each record cites a
fixture-local provenance entry that identifies the logical-schema sections and
discoveries being exercised.

Run:

```powershell
python scripts/validate_logical_schema_fixtures.py
```

The validator checks the four positive scenarios and applies one deliberately
invalid mutation to each as a regression check. These fixtures validate
relationships and invariants only; they do not assert that a disputed source
claim is an approved billing rule.
