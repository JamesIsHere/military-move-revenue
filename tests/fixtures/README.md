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

## Source/rule registry cases

`source-rule-registry/registry-cases.json` contains synthetic mutations of the
public-source-only registry. It verifies that archived artifacts and provenance
remain required, candidate web observations are not promoted without archival,
and open source conflicts block publication.

Run:

```powershell
python scripts/validate_source_rule_registry.py
```

## Initial scale-weight cases

`weight-determination/initial-scale-weight-cases.json` contains synthetic Item 4
boundary and regression cases. It stores exact weight values as JSON strings and
uses boolean presence markers instead of names, signatures, addresses, live
shipment numbers, or other sensitive ticket content.

Run:

```powershell
python scripts/validate_weight_determination.py
```

## Item 4.8 automatic-reweigh cases

`automatic-reweigh/item-4-8-cases.json` contains synthetic threshold cases for
E-1 through E-5, E-6 through O-10, and DoW civilian grade bands. It also verifies
that an unstated grade mapping and a blocked initial weight produce a blocked
decision instead of an inferred result.

Run:

```powershell
python scripts/validate_automatic_reweigh.py
```
