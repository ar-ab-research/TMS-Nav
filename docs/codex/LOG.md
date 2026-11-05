# Codex log

## 2026-10-21 — MRI reconstruction delivery and persistent handoff initialization

Implemented the end-to-end subject pipeline documented in
`docs/subject-reconstruction.md`; verification and limitations are recorded in
`docs/subject-reconstruction-report.md`. Important files include
`ingest_subject.py`, `src/subject_ingest.py`, `src/subject_coordinates.py`,
`src/fiducials.py`, `src/subject_registration.py`, `src/subject_qc.py`,
`src/synthetic_subject.py`, viewer integration and Python/Node/Playwright tests.

Verified during implementation in this thread:

- `micromamba run -n tms312 python -m pytest tests/ -q`: 66 passed.
- `cd viewer && micromamba run -n tms312 npm test`: 8 passed.
- `cd viewer && micromamba run -n tms312 npm run test:browser`: 1 passed.
- `cd viewer && micromamba run -n tms312 npm run build`: passed.
- MNI template rebuilt; synthetic marker detection, native coordinate/surface
  alignment, cache reuse and actual browser-to-Python correction round trip passed.
- Python 3.12.15 / Node 22.23.2 in user-local tms312; pip check passed.

Decisions: native RAS mm remains primary; underdetermined anatomy is explicit;
EEG requires confirmed anchors; no skull is inferred by scalp erosion. Detection
and registration remain reviewable estimates, not validated clinical measurements.
No private subject information is recorded in these checkpoints.

For the requested commit/push, read the newly supplied AGENTS.md. STATE.md and
LOG.md were absent and have been created. Reviewed tracked/untracked changes and
ignored data boundaries, confirmed git diff --check, and fetched origin. Branch
main and origin/main matched at base commit b1ef3ab before the delivery commit.
The latest browser test artifact also reports passed. No implementation changes
were needed for this commit-only task; the full test suite was not repeated.
This entry is included in the implementation delivery commit; its resulting hash
is discoverable with git log. Verify push success and synchronization directly
rather than assuming it from this log.

## 2026-10-22 — MRI review implementation started

- Read STATE/LOG/AGENTS and verified main at the existing delivery; user has a staged AGENTS.md change requiring `[codex]` commit prefixes. Preserve it.
- Implementing candidate rejection reasons, configurable bright/local filters and peak separation, cached loopback MRI/EEG API, NiiVue native slices and crosshair editing, and subject-only fiducials.
- Expected count five remains a QC expectation; no forced detections. Provisional EEG previews retain unconfirmed-anchor status.
- Added requested concise documentation policy to AGENTS.md. No real failing subject scan is present; requested its path while proceeding with synthetic verification.
- Tests/build are in progress; results pending.

## 2026-10-22 — MRI review verification and delivery

- Delivered `run_viewer.py`, `src/viewer_service.py`, `viewer/src/mriViewer.js` and `subjectReview.js`; updated detector, ingestion, editor and viewer integration.
- Found/fixed a faint synthetic sphere rejected as elongated when thresholded voxels occupied one plane: finite voxel-box covariance recovered marker five. Added configurable local contrast/physical filters and optional touching-peak separation.
- Normalized detector numeric types so browser/Python JSON retains stable candidate identity. Guarded late responses and metadata loading against replacing newer point edits; serialized MRI uploads.
- Live previews reuse the full scalp and retain provisional anchor confidence. Save persists reviewed inputs/derivatives and reuses existing registration; API reopening avoids static-bundle/HMR reloads.
- Verification: **75 Python tests, 8 JS tests, 2 Chromium/WebGL workflows**, production build, pip check and diff hygiene passed. Tests cover actual saved browser corrections, reopening, five unequal markers, MRI coordinates and cached EEG changes.
- Consolidated usage into the existing subject guide (177 lines); replaced the existing task report with latest changes/results and refreshed synthetic figures. Added concise documentation policy to AGENTS.md.
- User clarified that the real acquisition is restricted: do not search for or access it. A pending search was rejected after that instruction and was not retried. No private subject details are stored here; all demonstration artifacts are synthetic.
- Main and fetched origin/main matched at base **07fe146** before the `[codex]` delivery commit. Verify final commit/push directly; see Git history for the resulting task hash.

- Final synthetic visual QC isolated a non-preserved WebGL/MSAA reset capture artifact. MRI now retains complete frames without MSAA; a browser pixel check covers both halves of the sagittal phantom after reset.

## 2026-11-04 — Aim 1 positional comparison

- Implemented src/positional.py, compare_positions.py, viewer/src/positional.js, preparation/demo scripts and positional guide/report. Gray outer mesh verified as scalp in extraction and viewer code. Preserved unrelated datasetRegistry.js modification.
- Planned Targets only; text fallback records project/source/version/frame provenance; unresolved MRI identities/registration or trajectory semantics fail closed. Explicit SMA and right DLPFC/F4 mappings required.
- Public Rogue network/manual and SimNIBS material investigated; vendor protocol/examples and licensed runtime still needed to verify direct project/metadata retrieval. No guessed transport commands or binary parsing.
- Verified new tests (5), JS (21), production build and synthetic 5 mm demo. Initial full Python suite: 84 passed, HTTP socket test sandbox-blocked; authorized rerun pending. Patient anatomical/registration accuracy and new browser overlay interaction remain unvalidated.
- Generated only ignored local preparation/output artifacts. Supplied originals preserved. Usage and exact remaining inputs documented in docs/positional-comparison.md.

- Final verification: authorized full Python suite **85 passed**; subsequent nonidentity target-import/Samples-separation regression included in **6 positional tests passed**. Final viewer build passed.

- Implementation committed as 37e8dcc. Push to origin/main_ab rejected by automatic approval review because external destination/payload publication authorization was considered insufficient; no bypass attempted. Existing registry edit remains uncommitted.

## 2026-11-04 — Sidebar integration and local CLI-to-viewer flow

- Moved positional component into existing right Aim 1 sidebar with dark controls and tables. Added local report API and automatic loading/reload.
- Implemented --subject runner: actual cap triangle projections and explicit missing-data QC; reviewed manifests retain full comparison path. Filled known pending-manifest paths/hashes locally without inferring labels or registration.
- Read-only project inventory verified unresolved export/target/label/frame evidence; no binary coordinates decoded and no synthetic measurements substituted. Supplied files explicitly authorized by current user.
- Verified Python 88 passed, JS 21 passed, production build passed. Actual local browser workflow passed using installed Chrome; default Playwright Chromium absent. Final native-marker guard/style checks recorded below.
- Simplified docs/positional-comparison.md; updated report. Private outputs/screenshots ignored. Unrelated registry edit preserved. Prior rejected push not retried.

- Final checks: positional suite 8 passed after native-frame/unique-marker guards; actual local browser acceptance passed including dark-button style; final production build and git diff --check passed.

## 2026-11-04 — Supplied export rendered

- Imported newly supplied target export and added conservative autonomous site-name assignment with variant preservation and missing-site exclusion.
- Verified legacy scanner header codes; generated source-native scalp and rendered raw targets beside cap MRI with explicit independent frames. No undocumented trajectory interpretation or unverified cross-MRI overlay.
- Actual CLI and Chrome acceptance passed: target labels visible, source scalp loaded, rendered count correct, reload/toggles/export pass. Positional suite 10 passed; production build passed. Full suite result follows.
- Local API/viewer started (8765/1234) without registry regeneration. Existing staged registry edit preserved. Private artifacts ignored; prior blocked push not retried.

- Final full Python suite: **90 passed** (2 existing PyVista deprecation warnings). Browser and production build passed. Primary distances remain deliberately unavailable pending registration and semantics review.

## 2026-11-04 — Registered common-frame overlay and measurement gates

- Added src/brainsight_registration.py: rigid source-to-cap MI registration, explicit fixed-to-moving LPS inversion/conjugation, numerical QC and anatomical QC montage. Visually inspected technical alignment locally; patient accuracy remains unvalidated.
- Replaced side-by-side display with registered physical overlay. Six controls include source surface; sidebar QC resource and measurement table label added.
- Confirmed mapping/semantic gates and transformed segment intersection path implemented. Export metadata does not establish scalp contact or an inward trajectory; unresolved primary differences remain unavailable, never snapped/projected as a substitute.
- Persisted tms312 runtime requirement. Generated data/QC/review artifacts ignored; unrelated staged registry preserved; prior blocked push not retried.
- Verified: full Python 93 passed; final positional 13 passed; updated endpoint test passed; JS 21 passed; production build passed; actual Chrome overlay/toggle/QC/reload/export acceptance passed and screenshot inspected.

## 2026-11-05 — Unified LAYERS and unavailable-result audit

- Moved positional controls into existing LAYERS. Added green pyramid targets, red fiducials, single translucent red/green projection layer and lavender source scalp; removed annotation-only target display and duplicate right controls.
- Exploratory target projections explicitly labeled/exported; test confirms they cannot produce primary measurements. Expanded QC issue lists expose all input blockers, not only first exception; missing targets remain explicit.
- Verified real browser/pixel target-toggle check and inspected final screenshot. Build and JS 21 passed; full Python 93 passed before added regression, final focused 14 passed.
- Regenerated local data only; existing staged registry unchanged/excluded. Updated concise positional report/guide. tms312 used throughout. Prior blocked push not retried.

## 2026-11-05 — Confirmed pairing, projection endpoint and skin audit

- Persisted explicit user-confirmed pairing locally without changing raw points. Added documented CLI confirmation flag and separate projection endpoint; retained trajectory endpoint/gates and diagnostic variant.
- Provisional common-skin reconstruction from registered anatomical scan: no erosion/cosmetic smoothing, image-supported component/plane-hole filling. Rejected initial internal-interface candidate. Anatomical skin/hair/artifact review remains outstanding; no fabricated verification.
- Independent exhaustive triangle math confirms locator behavior; rigid separation/transform-once checks pass. Original projection discrepancy reflects competing near-equal surface regions. Audited display decimation and FOV edges. Generated per-fiducial anatomical slices and before/after mesh QC locally.
- Viewer shows provisional single-subject endpoint, raw/projected coordinates and offsets, separate trajectory results; expandable persistent parent/variant controls and labeled optional lines. Marker edits invalidate stale metrics. Added projection CSV and JSON provenance.
- Verification: Python full 96 passed; final focused 17 passed; JS 21 passed; production build and actual Chrome acceptance/pixel checks passed. All runtime work in tms312. Private artifacts ignored, unrelated staged registry preserved; prior blocked push not retried.

## 2026-11-05 — Accepted visual QC and GUI cleanup

- User accepted the result after reviewing rendering/QC. Saved acceptance against exact local surface hash, scoped to visual QC, and changed current result display/export to REVIEWED. Clinical accuracy remains a separate limitation; plots and numerical results retained.
- Brainsight targets now spheres centered at raw MRI-world coordinates. Removed legacy Aim 1 metrics/results HTML and stale review-code references; newer comparison sections retained.
- Verified focused Python 16 passed, JS 21 passed, actual Chrome acceptance/pixel checks passed, final build passed. An initial browser check found a stale removed-panel reference; corrected and rerun cleanly. Screenshot visually inspected.
- Updated existing report/usage. All runtime work used tms312; private review/data artifacts ignored. Prior blocked push not retried.

## 2026-11-05 — Viewer launcher cache repair

- Clean main_ab at task start. Reproduced actual Parcel failure resolving obsolete ./sources.js; no current source import exists. Fresh cache built successfully.
- run_viewer.py now uses a temporary per-session Parcel cache and propagates npm status; usage/report updated. Added tests/test_run_viewer.py covering cache isolation/removal, status and API shutdown.
- Verified tms312 launcher regression: 1 passed; actual launcher build 1.09 s, viewer HTTP 200, API /api/health HTTP 200. Verification servers stopped. Full suite not repeated.
- Initial sandbox run could not bind loopback; authorized local verification completed. No private artifacts added.
- Delivery commit: c7ab497. Automatic approval review rejected combined commit/push because the remote destination was unverified and could expose private code. Local-only commit succeeded separately; push was not retried.
