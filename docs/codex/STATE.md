# Codex state

Updated: 2026-11-04

## Current objective
- Implement Aim 1 positional scalp comparison; independent work delivered, individualized validation pending.

## Completed work
- `src/positional.py`, `compare_positions.py`, viewer positional panel; explicit mappings, target-only text fallback, strict frame/registration gates, triangle projection, directed scalp intersections, QC/statistics/exports.
- Synthetic demo and local input preparation; docs/positional-comparison.md and report.
- Confirmed gray mesh is scalp; skull stays separate. No assumed SMA=Cz or marker ordering.

## Verified results and tests
- New positional tests: 6 passed; existing JS suite: 21 passed; viewer production build passed.
- Synthetic 5 mm demo and pending local manifest generation succeeded.
- Full Python suite: 85 passed after granting loopback access; added adapter regression then positional suite: 6 passed.

## Decisions and assumptions
- Latest user explicitly authorized supplied local project/anatomical inputs, superseding prior restriction for this task only. No private values or data are committed.
- Direct .bsproj/network retrieval unsupported until vendor protocol and licensed application validate capabilities. Text fallback is explicit.
- Raw target cannot generate primary comparison without documented trajectory or scalp-point semantics.

## Uncommitted changes
- Implementation/docs/tests delivered in [codex] commit (verify hash in Git). Existing unrelated datasetRegistry.js change remains untouched and excluded.

## Blockers and next actions
1. Obtain planned-target text export from supplied project, exact marker/target mappings, image-frame and trajectory evidence; complete local pending manifest.
2. Run CLI, inspect in viewer, compare independent export with precision-based tolerance; validate anatomy/registration separately.
3. Obtain vendor network schema/examples and licensed Brainsight to establish direct project retrieval support.
4. Add automated browser test for new overlay interaction. Implementation commit: 37e8dcc. Push to origin/main_ab rejected by automatic review: external destination/payload publication authorization needs confirmation.
