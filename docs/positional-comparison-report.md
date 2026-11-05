# Positional component implementation report

- Implemented strict planned-target text adapter with `.bsproj` entry/fallback distinction, preserved source fields/orientations, MRI identity and registration gates.
- Implemented triangle projection, verified directed segment/scalp intersection, explicit mappings, raw-position retention, Euclidean mm comparisons, invalid-pair QC, per-target summaries and CSV/JSON.
- Added existing-viewer overlays with five independent toggles, subject/MRI/marker checks, distance/method/QC display and exports.
- Confirmed gray mesh is scalp (`src/head_surface.py:scalp_surface`); skull is separate and never used by the comparison CLI.
- Added CLI, synthetic numerical demo, and local supplied-input preparation. Originals preserved; no subject data tracked.
- Documentation: `docs/positional-comparison.md` contains installation, API/CLI, formats, network capability investigation, settings and validation procedure.

## Verified

- New positional tests: 6 passed (geometry, coordinate transforms/units/flips, intersections, invalid pairs, adapter gates, export precision and outputs).
- Synthetic demo generated two 5 mm comparisons; local input preparation generated a pending manifest successfully.
- Existing JS suite: 21 passed. Production viewer build passed.
- Full Python run: 85 passed after loopback authorization; subsequent added adapter regression verified with positional suite (6 passed).

## Unvalidated / remaining limitations

- Direct binary/network extraction is unavailable; no undocumented binary fields or endpoints guessed. Vendor protocol/examples and licensed Brainsight access are needed to verify supported direct-project operations. Public material confirms TCP functionality, not every requested retrieval capability.
- Supplied project cannot yield a valid individualized comparison without export, mappings and frame/trajectory evidence. Local pending manifest deliberately fails until resolved.
- Viewer controls built successfully; new overlay flow has not received an automated browser interaction test.
- Numerical import agreement is distinct from anatomical or registration accuracy. Independent same-project export and patient review remain pending.
- Existing unrelated `viewer/src/datasetRegistry.js` modification preserved and excluded from commit.
