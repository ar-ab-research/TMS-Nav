# Codex state

Updated: 2026-11-05

## Current objective / completed
- User-confirmed cap-SMA/exact planned SMA pairing persisted in ignored review JSON; CLI confirmation flag documented and executed. Original marker positions unchanged; diagnostic target variant stays separate.
- New projection-based SMA endpoint uses closest triangle points on one full-resolution common candidate surface. No trajectory/contact gates; separate trajectory endpoint preserved. Unverified skin/alignment yields a clearly provisional preview, not a verified anatomical result or cohort statistic.
- Added independent NumPy triangle audit, rigid-separation/once-only transform checks, competing-region diagnostics and display-decimation checks.
- Audited original head mask; constructed alternative from registered apparently cap-free image with intensity evidence/component/hole filling and no erosion/cosmetic smoothing. First candidate with internal interfaces rejected; revised candidate remains anatomically unverified. Slice QC at marker/target and other fiducials, plus old/new mesh controls.
- Expandable persistent Brainsight parent/variant raw/projected toggles; labeled projection/endpoint lines; displayed raw/projected coordinates and offsets; projection CSV export and stale-marker invalidation.

## Verified
- Full Python suite 96 passed. Final focused projection/API suite 17 passed; JS 21 passed; final build passed.
- Actual Chrome acceptance passed: provisional endpoint, selected-skin loading, parent/variant persistence, raw/projected toggles, reload/export and rendered target pixel check.
- Independent geometry agrees with VTK; transform preserves raw distances. Old discrepancy is nearest-region sensitivity, not a demonstrated transform/locator bug. Detailed deidentified results are in requested task report, not checkpoints.
- All detected open-edge vertices verified at scan FOV boundary. Skin-only interpretation and patient accuracy still unverified. Data, mappings, images and meshes remain ignored locally.

## Decisions / blockers
- Precise remaining blocker to verified projection result: anatomical review/correction of common skin, including hair ambiguity, local artifacts and FOV truncation; surface review bound to exact mesh hash.
- Trajectory semantics do not gate projection metric; still gate separate entry endpoint. Missing site remains absent.
- Use micromamba tms312 for Python/Node. Existing staged datasetRegistry.js edit preserved/excluded. Prior external push rejection unresolved; no retry/bypass.

## Next actions
1. Refresh local viewer, choose subject and Reload analysis. Usage guide documents explicit confirmation command and normal reruns.
2. Review local skin slices/full mesh and registration; supply corrected reviewed skin if required. Do not set verified solely to clear provisional label.
3. Inspect delivery commit in Git; task files committed with [codex] prefix. Independent patient/export validation remains separate.
