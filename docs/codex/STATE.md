# Codex state

Updated: 2026-11-04

## Current objective
- Sidebar integration and simplified CLI-to-viewer positional workflow delivered; individualized target measurements await explicit data evidence.

## Completed
- Positional component moved below existing right-sidebar content with matching dark controls/tables; automatic local API report loading, reload and exports.
- `compare_positions.py --subject SUBJECT` generates actual cap projections/input-QC or runs reviewed comparison manifest. Preparation fills known paths/hashes; preserves originals/review fields.
- Read-only project schema/name inventory only; no undocumented coordinate blob interpretation.
- Local supplied-input report generated and rendered in actual browser. Usage guide simplified; positional report updated.

## Verified
- Full Python suite: 88 passed; final native-marker guard verified by focused suite (8 passed). JS: 21 passed. Final production build passed.
- Local browser acceptance passed, including dark-style assertion, automatic sidebar results, toggles, reload, download and no exceptions.
- Generated subject reports, manifests and screenshots are ignored and uncommitted. No patient details in checkpoint documents.

## Decisions / assumptions
- User authorized local supplied subject files. Different anatomical images require verified registration; marker ordering and approximate proximity do not establish labels.
- Licensed Brainsight unavailable; project export and documented scalp/trajectory semantics required for measurements. QC/projection reports never claim completed target-distance analysis.

## Uncommitted changes
- This task's code/tests/docs delivered in [codex] commit; verify hash with git log.
- Existing unrelated viewer/src/datasetRegistry.js remains uncommitted, untouched by task edits.

## Blockers / next actions
1. Obtain planned Targets text export, explicit SMA/F4 marker mappings, required planned target(s), verified registration and scalp-point/trajectory evidence. Complete local pending manifest, save as manifest.json, rerun --subject.
2. Inspect numerical agreement with independent export separately from anatomical accuracy.
3. Previous push rejected by automatic review: external destination/payload publication requires approval. Do not retry/bypass without resolving authorization.
