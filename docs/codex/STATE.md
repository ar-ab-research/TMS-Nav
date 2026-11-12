# Codex state

Updated: 2026-11-12

## Current objective
- Completed merge repair on `main_ab`: restore public Ernie, isolate subject rendering, verify Aim 2 and protect local data. Follow-up authorizes a **local commit of all changes; no push**.

## Completed work
- Follow-up: demo landmark edits preserve checked EEG/arcs; prior calculation explicitly labeled. Preview pending/error also retains prior visible layers. Browser landmark storage untouched.
- Public Ernie Aim 1/four Aim 2 outputs restored locally from public deployment Git snapshot `04263d28d0cd3e4e549e5bd9bb57a7fee0e3a5c8`; reproducible `scripts/restore_public_ernie.mjs`.
- `viewer/src/main.js`, `positional.js`: switch clears positional groups/pending requests and restores selected subject scalp; new regression coverage.
- Registry separation: tracked `datasetRegistry.js` public heads only; ignored `datasetRegistry.local.js` all local heads. `scripts/refresh_viewer_registry.py` runs before npm dev/build.
- Existing guides updated; details in `docs/subject-rendering-report.md`.

## Verified results
- Python: 104 passed in full run; one sandbox-blocked HTTP test passed separately with permission (105 total).
- JS: 27 passed; production build passed.
- Chrome: three relevant tests passed together, including four landmark edits, reload persistence and actual EEG/arc toggle pixel differences; positional switch and Aim 2 checks also passed. JS 27 and final production build passed again.
- Public deploy guard rejects mixed private workspace; generated data/local registry ignored; public registry excludes private subject. Staged/working whitespace checks passed.

## Decisions / assumptions
- tms312 for Python/Node/npm; sandbox needs XDG_CACHE_HOME=/tmp/tms-cache and loopback/LMDB permission for verification.
- Public deployment output restores demo viewing without installing SimNIBS or rerunning FEM.
- Local builds include private heads and must stay local. Use public deploy guard; never force-add ignored assets.
- No new patient accuracy or registration validation. Prior anatomical/handle/current limitations remain; see positional and Aim 2 guides/reports.

## Uncommitted changes
- User started with many staged manually merged remote changes; preserved them.
- Follow-up requests committing all merged and task changes together. Local commit prepared after verification; no push. Check Git history for delivery hash.
- Ignored restored public assets coexist with private local datasets.

## Remaining blockers
- None for requested fixes. Full browser suite and fresh FEM simulation not run.

## Specific next actions
- Keep the current browser profile to retain the user-picked Ernie landmarks; export JSON for a separate copy. They are local browser data, not committed assets.
1. Launch `micromamba run -n tms312 python run_viewer.py`; Ernie opens by default, use `#aim2` for fields.
2. Review merged/task changes before preparing PR. Keep ignored artifacts excluded.
3. For public deployment, use a clean workspace containing only allowlisted heads; never publish this local dist.
