# Aim 1 layers and unavailable-result audit

## Changes

- Added Brainsight MRI surface, Brainsight targets and one combined scalp-projection control to the existing left **LAYERS** panel. Removed duplicate right-side layer controls; choices persist across reloads.
- Brainsight targets are green pyramids; MRI fiducials are red diamonds. Closest-triangle projections use translucent matching green/red spheres. Source MRI surface is lavender; template targets orange; existing coil blue, EEG cyan and landmarks yellow remain distinct.
- Source extraction is labeled **scalp**, not cortical brain: no validated cortical segmentation was supplied.
- Added Brainsight target projections as explicitly **exploratory** display data. They never become verified entry points or enable primary distances. Raw coordinates remain unchanged.
- Disabled verified-entry/line controls when no valid pairs exist. Expanded QC diagnostics so the table lists every known blocker instead of only the first exception.

## Why fields are unavailable

| Field | Verified cause | Required resolution |
|---|---|---|
| SMA / SMA Skin localization difference | No identity-bound `comparison/review.json`; cap marker mapping unconfirmed; no documented planned scalp point or verified inward segment. Skin-named raw target is off the common scalp. | Confirm exact cap/target mapping and supply documented scalp/trajectory semantics. A name or exploratory projection is insufficient. |
| Right DLPFC / F4 difference | Export contains no corresponding planned target. | Supply the actual target; do not reuse SMA. |
| Derived entries and comparison lines | No valid primary pairs, so no derived geometry exists. | Resolve the above inputs. |

Registration and imported raw-target rendering succeeded; they are not causing these unavailable results. Invalid pairs remain excluded from summaries.

## Validation

- Actual local report regenerated; raw/registered points and exploratory projection data retained locally.
- Positional suite: 14 passed, including proof that exploratory projection cannot enable a primary measurement. Full suite: 93 passed before adding that regression.
- Production build passed. Actual Chrome LAYERS visibility/persistence, pyramid geometry, projection count and canvas-pixel toggle check passed; final screenshot inspected. JS suite: 21 passed.
- Private data/reports/screenshots ignored; unrelated staged registry change preserved. Prior blocked push not retried.
