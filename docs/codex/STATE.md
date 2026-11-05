# Codex state

Updated: 2026-11-05

## Current objective / completed
- Consolidated positional visibility controls in left LAYERS: registered source scalp, green pyramid targets, and combined red/green translucent projection spheres; removed duplicate right-side controls/target annotations.
- Fiducials red diamonds; source surface lavender; template targets orange; existing coil/EEG/landmark colors remain distinct. Accurate scalp labeling, no claimed cortical segmentation.
- Added labeled exploratory Brainsight closest-triangle projections to local JSON/CSV, without promoting them to verified entries or primary distances.
- Expanded per-target QC reasons; disabled geometry controls when no verified pairs exist. Concise unavailable-result audit in existing positional report.

## Verified
- Full Python suite 93 passed before final added projection-gating regression; focused positional suite 14 passed including it.
- Actual Chrome acceptance/pixel toggle check passed; screenshot inspected for visible pyramids, colored projections and left controls. Production build passed; JS suite 21 passed.
- Local CLI regenerated outputs. Generated patient data/projections/screenshots remain ignored; no private details stored in checkpoints.

## Assumptions / blockers
- Primary measurements still require identity-bound confirmed marker mapping and documented scalp point/inward segment; missing site remains absent. Registration/rendering are not the reason for unavailable differences.
- New nearest-point target projections are exploratory visualization only.
- Use micromamba tms312 for all Python/Node work.

## Uncommitted changes / delivery
- Task files delivered in [codex] commit; verify hash in Git.
- Existing staged viewer/src/datasetRegistry.js preserved/excluded. Previous automatic-review rejection of external push unresolved; no retry/bypass.

## Next actions
1. Refresh local viewer; select subject and Reload analysis. Left LAYERS controls all visibility.
2. Complete confirmed mapping/entry semantics when available; validate independent export and patient anatomy separately.
