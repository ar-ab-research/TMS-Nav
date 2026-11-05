# Positional comparison delivery report

## Latest changes

- Moved the positional component below the existing right-sidebar content, within the Aim 1 tab. Reused dark controls, typography, separators and tables; removed floating bottom-left panel and raw JSON summary display.
- `python compare_positions.py --subject SUBJECT` now produces a local report from supplied inputs, or runs a reviewed `comparison/manifest.json` when available. The viewer automatically fetches it through the existing local API; Reload analysis refreshes it without file import.
- Actual local subject report generated: original cap points preserved, closest-triangle projections rendered, missing comparisons explicitly unavailable. No synthetic targets substituted.
- Read-only SQLite inventory identifies target names without decoding undocumented coordinate blobs. Inspection established concrete missing export/label/target/registration/trajectory evidence. No licensed Brainsight installation was found.
- Preparation fills known local paths/hashes while preserving review fields and explicit mappings. Supplied originals untouched; all reports/manifests/screenshots remain ignored local artifacts.
- Rewrote usage guide around two commands, output locations, viewer behavior and concrete remaining inputs.

## Verification

- Full Python suite: **88 passed** before final native-marker guard; focused suite rerun after that guard: **8 passed**.
- JavaScript: **21 passed**.
- Viewer production build passed.
- Actual local subject Playwright acceptance test passed: automatic sidebar loading, report/marker rows, five toggles, reload, JSON download, no browser exceptions. Final dark-style assertion rerun passed.
- Playwright's default downloaded Chromium was absent; used installed Chrome via `PLAYWRIGHT_CHANNEL=chrome`. Optional local acceptance test skips when private input/report files are absent.

## Remaining

- Full individualized distances require the planned-target export, explicit marker mappings, correct planned targets and reviewed source-to-marker MRI registration/trajectory semantics. Current report is an input-QC/projection result, not a completed target-distance measurement.
- Direct .bsproj coordinate retrieval and anatomical/registration validation remain unavailable/unvalidated as described in the usage guide.
- Pre-existing datasetRegistry.js edit preserved and excluded from delivery.
- Previous external push remains blocked by automatic review pending destination/payload publication approval; no retry or bypass in this task.
