# Current State

## Status

Active. The domestic DP3 TSP-to-government post-audit goal remains ratified.
M1 source closure is externally constrained, M2's logical contract is complete,
and M3 contains two published deterministic reference packages plus a
conflict-aware draft registry.

## Active milestone

M1 — Establish the source foundation remains active for current PPA and
source-version gaps. M3 — Implement the source and rule registry is advancing
from reviewed 400NG/Tender material. M4 monetary shadow rating has not started.

## Last checkpoint

The current repository checkpoint includes the physical source/rule registry,
initial-weight and Item 4.8 executable reference packages, post-reweigh source
reconciliation, and CF-0004. Use `git log -1 --oneline` for its commit ID; the
working tree should be clean at cold resume.

## Completed

- Ratified the domestic DP3 post-audit goal and 25-case historical completion
  verifier; archived and checksummed nine public source artifacts.
- Recorded 91 discoveries, the conceptual/logical contract, Decision 0002, and
  the source-conflict workflow.
- Added the file-backed physical registry and validator with archive hash checks,
  provenance, dependencies, evidence requirements, and publication gates.
- Published and implemented `2026.weight-determination.1`; 14 synthetic initial
  weight/evidence cases pass.
- Published and implemented `2026.automatic-reweigh.1`; ten Item 4.8 threshold,
  blocked-input, and tampering cases pass.
- Rendered and visually verified the controlling-weight/refund passages on
  400NG pp. 19 and 22-23 and Tender printed p. 20; checked DTR A-402 section
  D.7.b for operational evidence.
- Added ten reviewed claims (`CLM-0023`-`CLM-0032`) for reweigh fee eligibility,
  lower-weight invoicing, constructive weight, refunds/billing holds,
  containerized provisional/correction paths, duplicate reweighs, and DPS/ticket
  evidence.
- Documented that the Tender's general lower-weight obligation and 400NG's
  narrower fee/workflow provisions are scoped and additive, not directly
  conflicting.
- Registered `CF-0004` for the unstated weight fact that selects the 5,000-lb
  reweigh-tolerance branch. Two affected tolerance rules remain draft and
  blocked; the general lower-weight model is not blocked.

## Current task

Model immutable completed and duplicate reweigh observations, including gross,
tare, net, weighing date, ticket evidence, DPS update, source provenance, and
supersession. After that model is exercised synthetically, implement only the
non-tolerance lowest-completed-net selection. Do not implement fee or
containerized reimbursement tolerance through CF-0004.

## Known blockers

- CF-0004: the governing text does not identify the weight fact selecting the
  5,000-lb tolerance branch.
- Direct archival requests to PPA.mil and media.defense.gov returned HTTP 403.
- The mileage/SIT tool effective period, authorized-SIT percentage/rounding, and
  current domestic item-code supersession chain remain unresolved.
- Final acceptance requires at least 25 authorized, anonymized historical cases
  with independently approved outcomes.

## Decisions needed

- Resolve CF-0004 before publishing reweigh-fee or containerized-reimbursement
  tolerance logic.
- Resolve CF-0001 before SIT/accessorial rate-date selection.
- Resolve CF-0002 before the disputed transit/SIT-tool behavior.
- Resolve CF-0003 before treating the 2022 item-code workbook as authoritative
  for 2026.
- Later, select the first monetary charge family for shadow rating.

## Next three actions

1. Add synthetic immutable reweigh-observation records and validation, including
   duplicate reweighs and late corrections.
2. Implement the reviewed non-tolerance lowest-completed-net selection with
   explicit ticket and DPS-update evidence.
3. Continue pursuing archivable current PPA source artifacts.

## Verification status

The physical registry now contains 29 archived-source claims, 27 locators, four
open conflicts, three packages, and eleven rules: six disputed drafts, four
published initial-weight rules, and one published automatic-reweigh rule. The
registry validator passes one valid case and seven expected failures. Initial
weight (14 cases), automatic reweigh (10 cases), and logical-schema validation
pass. No completed-reweigh selector, tolerance result, fee, refund amount,
billing item, expected invoice amount, or SIT result is implemented. Current
registry and executable-reference work is included in the current checkpoint.
