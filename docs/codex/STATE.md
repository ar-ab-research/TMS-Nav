# Codex state

Updated: 2026-11-04

## Objective / completed
- Registered Brainsight source MRI to cap MRI; removed side-by-side layout and viewer translations. Surfaces/raw points overlay in cap RAS mm with independent controls.
- Added rigid registration/QC module, hash-bound cache and technical anatomical-review evidence locally. Primary measurements use common cap scalp only.
- Confirmed mapping/registration/semantic gates; verified segment transforms/intersections; explicit missing sites. Skin name never establishes entry semantics.
- Sidebar and export measurement label: scalp-entry localization difference (mm). QC image and review template available locally.
- Persisted user requirement: Python and Node/npm work must use micromamba tms312 (also in AGENTS.md).

## Verified
- Full Python suite 93 passed; final focused suite 13 passed; updated API endpoint test passed.
- JS 21 passed; production build and actual Chrome overlay/QC/toggle/reload/export acceptance passed. Visually inspected registration and single-head overlay.
- Technical registration alignment reviewed; independent patient accuracy unvalidated. No private data/coordinates in checkpoints; generated artifacts ignored.

## Decisions / blockers
- Primary distances unavailable until exact cap marker mappings and planned scalp/trajectory semantics are confirmed; missing target remains absent.
- Never substitute raw nearest-point projection for an unverified Brainsight entry. Separate numerical agreement from anatomical accuracy.
- Existing staged viewer/src/datasetRegistry.js unrelated edit remains preserved and excluded.
- Prior automatic-review rejection of external push remains unresolved; do not bypass/retry without authorization resolution.

## Next actions
1. Complete local review template with identity-bound confirmed mapping and documented entry semantics when available; rerun --subject and Reload analysis.
2. Validate coordinates against independent export and review registration/anatomy independently.
3. Inspect delivery commit in Git; all task files committed with [codex] prefix.
