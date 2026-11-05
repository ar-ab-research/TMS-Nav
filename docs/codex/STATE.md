# Codex state

Updated: 2026-11-04

## Objective / completed work
- Supplied planned-target export now imports and renders on its source MRI scalp beside cap MRI in existing HTML viewer; autonomous conservative site-name mapping added.
- Legacy scanner-frame exports accepted only with verified scanner header codes; names/orientations/source positions/provenance retained.
- Extracted/cached source-native scalp; labeled independent frames and raw points. No invented common-frame overlay or cross-MRI distance.
- CLI regenerated real local outputs. Local API/viewer started on 8765/1234 without overwriting registry.

## Verified
- Actual Chrome acceptance passed: imported labels visible, source scalp loaded, count matches import; reload, toggles, export, no exceptions.
- Full Python suite: 90 passed; positional tests: 10 passed. Chrome acceptance and production build passed.
- Data, derivatives and screenshots remain ignored. No private coordinates/subject details in checkpoints.

## Decisions
- User authorized autonomous Brainsight-name-to-site mapping; preserve variants, leave unmatched names unassigned and missing target absent. Does not establish cap marker identity or scalp semantics.
- Distinct MRI frames displayed separately until verified registration; display separation never becomes a measurement.

## Uncommitted changes
- Task implementation/tests/docs delivered in [codex] commit; verify hash in Git.
- Pre-existing staged viewer/src/datasetRegistry.js remains excluded and unchanged.

## Blockers / next steps
1. Review cap marker identities and planned scalp/trajectory semantics; verify source-to-marker registration for primary positional comparisons.
2. Acquire missing site target when available; validate numerical import independently of anatomy/registration accuracy.
3. Prior push rejected by automatic review: destination/payload publication approval unresolved. No retry or bypass.
