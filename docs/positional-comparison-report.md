# Aim 1 registered-overlay implementation report

## Implemented

- Persisted `tms312` runtime requirement in AGENTS.md; all Python/Node work for this task used that environment.
- Added deterministic source-to-cap rigid MRI registration, explicit LPS/RAS and direction conversion, inverse/determinant checks, hash-bound cache and before/after anatomical QC montage.
- Inspected actual anatomical QC: brain boundaries, midline and ventricles align across nine registered views. Recorded technical agent-review evidence locally; independent patient/clinical accuracy remains unvalidated.
- Removed side-by-side layout and display offsets. Source surface/points are transformed physically into cap MRI RAS mm; common cap mesh remains the measurement surface. Added independently toggleable translucent registered surface.
- Preserved raw target positions/orientations and transformed copies. Export has no documented scalp-entry designation or inward planned segment; a named Skin target is not accepted on name alone. Raw distance-to-scalp diagnostics do not substitute a scalp entry.
- Added confirmed marker mapping, MRI identity, registration-review and semantic gates. Source-frame verified segment endpoints are transformed into cap frame before direction/intersection checks. Missing sites remain explicit and excluded.
- Top imported-target table and exports use **scalp-entry localization difference (mm)**. Valid measurements retain compatibility distance fields and add `scalp_entry_localization_difference_mm`. Unresolved measurements remain unavailable.
- Added sidebar registration QC images and local review-template generation; updated existing usage guide.

## Verification

- Full Python suite: **93 passed**. Final positional suite: **13 passed**; endpoint test passed after adding registered-surface/QC resources.
- JS suite: **21 passed**. Production viewer build passed.
- Actual Chrome acceptance passed: registered target overlay, six independent controls, source-surface toggle, QC image loading, reload and export. Inspected actual screenshot; single overlaid head, no layout translation.
- Known-distance, nonidentity registration direction, LPS/RAS, transformed trajectory, missing-target, unconfirmed-mapping and false Skin/scalp-contact tests passed.
- Generated registration files, reports, images and templates remain ignored locally. Unrelated staged registry edit preserved.

## Unresolved

- Supplied planned entry semantics and cap-marker identities are not confirmed. Skin-named raw position is off the common scalp. Primary distances therefore remain unavailable; no exploratory projection was substituted.
- Missing planned site requires its actual target, not another site's target.
- Independent export validation and patient anatomical/registration validation remain pending.
- Prior external push rejection remains unresolved; no retry/bypass attempted.
