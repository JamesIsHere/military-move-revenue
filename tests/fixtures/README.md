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

The validator checks eighteen positive scenarios and applies deliberately
invalid mutations as regression checks. These fixtures validate relationships
and invariants only; they do not assert that a disputed source claim is an
approved billing rule.

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

The Item 28B facts scenario preserves an actual-pickup performance date, one
Government-authorized completed extra-delivery occurrence before final delivery,
and reviewed authorization and completion evidence. It intentionally contains
no monetary result; the published rule package produces that result.

The Item 130 non-monetary scenario exercises the ratified revised fact model
with a synthetic 250-cc motorcycle, reviewed classification and measurement
evidence, immutable handling performances, Government preapproval, and a
non-billable loading/unloading pairing candidate. It intentionally leaves the
candidate service family and approver role unmapped and contains no billing
code, service definition, billable quantity, rate, amount, or financial result.
Five negative probes reject money, premature service mapping, missing evidence,
in-place supersession, and a changed measurement boundary.

The Item 130G television-boundary scenario compares three evidence-backed facts:
an exact 48-inch non-flat positive candidate, a 47.999-inch non-flat article
below the threshold, and an exact 48-inch flat-screen exclusion. Five negative
probes reject threshold drift, either excluded article being auto-classified,
missing classification evidence, and inserted money.

The Item 130I/130J volume-and-assembly scenario uses a playhouse and a hot tub to
test both tariff families independently. For each family, an assembled article
at 100.001 cubic feet is a reviewed positive candidate, an assembled article at
exactly 100 cubic feet has no candidate, and an over-100 article moved
disassembled has no candidate. Six negative probes protect the strict threshold,
assembled-state gate, reviewed evidence, and no-money boundary.

The Item 130C-130F boat-boundary scenario preserves reviewed canoe, jet-ski,
kayak, boat, dinghy, and boat-trailer facts with present, absent, and unknown
trailer states. Exact decimal measurements test disregarding fractional feet,
physical center-line and manufacturer methods, the 14-foot and 16-foot
classifications, width/height OTO context, and HHG co-move context. The 130E
listing-subtype and 130F BOTO-program gaps remain open and provenance-linked.
Nine negative probes reject boundary or measurement-method drift, collapsed
trailer states, invented 130F classification, changed HHG/BOTO context, removed
conflict gates, and inserted money.

The Item 130 exclusion-and-approval scenario keeps Code 2, crating approval,
crating performance, one-person hand-carry, standard-carton transport, and
shuttle transload as distinct evidence-backed facts. Canoe, kayak, and dinghy
facts exercise the tariff's named hand-carry/carton exceptions. Six isolated
handling performances prove that only timely, approved, reviewed Government
preapproval clears the non-financial fact-readiness gate; missing, denied,
conflicting, late, and unreviewed approval remain separately identifiable.
Twelve negative probes protect those distinctions, the unmapped service and
approver profiles, and the no-money boundary.

The Item 130 handling-and-SIT-pairing scenario preserves reviewed zero, one,
multiple, unmatched-loading, unmatched-unloading, and duplicate pairing states.
Duplicate references remain conflicting rather than becoming a count. Three
additional factual pairs retain distinct TSP-convenience, non-TSP-convenience,
and unknown SIT causes. The tariff-versus-item-code combined-service gap and
`CF-0001`/`CF-0003` remain open; no service mapping, billable quantity, rate,
amount, rule, reconciliation, or audit output is produced. Twelve negative
probes protect cardinality, article identity, chronology, SIT linkage and cause,
conflict/evidence gates, and the no-money boundary.

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

## Item 28B extra-delivery cases

`item-28b-extra-delivery/item-28b-cases.json` applies the scoped contract from
Decision 0004 / `INT-0002`. It covers both effective-period boundaries,
actual-versus-requested date selection, occurrence eligibility, Government
authorization, reviewed evidence, exact multi-occurrence arithmetic, malformed
facts, duplicates, and result-package tampering.

Run:

```powershell
python scripts/validate_item_28b_extra_delivery.py
```

## Item 28B post-audit cases

`item-28b-post-audit/item-28b-audit-cases.json` combines published Item 28B
rating results with immutable corrected invoice/payment history. It covers
expected, missing, unsupported, under/overbilled, quantity, payment, mapping,
completeness, evidence, chronology, malformed-input, and result-tamper paths.

Run:

```powershell
python scripts/validate_item_28b_post_audit.py
```
