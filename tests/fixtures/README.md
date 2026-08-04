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

The validator checks the eight positive scenarios and applies one deliberately
invalid mutation to each as a regression check. These fixtures validate
relationships and invariants only; they do not assert that a disputed source
claim is an approved billing rule.

The reweigh-observation scenario preserves two completed reweighs as distinct
observations and models a late correction as an immutable superseding version.
It verifies exact gross/tare/net arithmetic, ticket evidence, and DPS-update
fact coverage without selecting a controlling weight or applying a tolerance.

The constructive-weight facts scenario verifies positive cubic volume, reviewed
volume evidence, a supported eligibility reason, responsible-PPSO approval, and
either a published valid-ticket result or documented ticket unavailability. It
does not execute the 7-lb-per-cubic-foot rule.

The containerized-reweigh facts scenario preserves original tare, later new
gross, and still-later new tare as separate ticketed observations. The
provisional inputs are ready for a deterministic rule, while reimbursement
tolerance remains explicitly blocked by `CF-0004`.

The reweigh-refund workflow scenario preserves an approved original invoice and
a separate negative-supplemental identity, then records the completed reweigh,
DPS update, PPSO ticket delivery, refund-required/submitted/processed chain, and
destination/direct-delivery hold lifecycle. It contains no calculated refund,
tolerance, fee, expected charge, reconciliation, or payment result.

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

## Completed-reweigh selection cases

`completed-reweigh-selection/lowest-current-net-cases.json` reuses the synthetic
immutable reweigh history and verifies current-version selection, corrected
observations, exact decimal comparison, ties, missing measurement/evidence/DPS
facts, incomplete corrections, malformed supersession, binary numeric rejection,
and result-package tampering.

Run:

```powershell
python scripts/validate_completed_reweigh_selection.py
```

## Initial-versus-reweigh lower-reference cases

`scale-reweigh-lower-reference/lower-weight-cases.json` builds real upstream
results from the synthetic initial-weight and immutable reweigh fixtures. It
verifies lower initial, lower reweigh, equal-weight ties, exact fractional
comparison, one or two blocked upstream results, unit and provenance tampering,
unknown upstream packages, and result-package tampering.

Run:

```powershell
python scripts/validate_scale_reweigh_lower_reference.py
```

## Constructive-weight reference cases

`constructive-weight-reference/constructive-weight-cases.json` builds a real
valid-ticket upstream result and combines it with the synthetic volume and PPSO
approval facts. It covers exact fractional multiplication, lower ticket, lower
constructive weight, ties, documented lost tickets, blocked volume/approval/
upstream evidence, unit and provenance errors, mismatched result references, and
result-package tampering.

Run:

```powershell
python scripts/validate_constructive_weight_reference.py
```

## Containerized provisional-weight cases

`containerized-provisional-weight/provisional-weight-cases.json` combines a
real final initial-weight result with the synthetic containerized original-tare
and new-gross observations. It covers exact subtraction, lower initial, lower
provisional, ties, later-new-tare isolation, evidence and readiness blocks,
nonpositive provisional inputs, unit and chronology errors, upstream provenance,
and result-package tampering.

Run:

```powershell
python scripts/validate_containerized_provisional_weight.py
```

## Reweigh refund-workflow cases

`reweigh-refund-workflow/workflow-cases.json` builds a real initial-weight,
completed-reweigh, and lower-reference result chain before evaluating the
post-invoice workflow. It covers refund-required and not-required branches,
ready and not-ready holds, conditional refund processing, DPS and PPSO evidence
blocks, chronology, upstream provenance, result references, and tampering.

Run:

```powershell
python scripts/validate_reweigh_refund_workflow.py
```
