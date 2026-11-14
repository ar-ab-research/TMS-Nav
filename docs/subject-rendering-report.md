# Viewer merge repair report

Updated: 2026-11-12. Branch: `main_ab`. Follow-up authorizes a local commit of all changes; no push.

## Changes

- Follow-up: landmark edits no longer force electrodes/arcs off or block their checkboxes. Previous calculations remain visible with an explicit status until an individual-subject preview replaces them. Restored demo edits keep that status after reload. Existing browser landmark storage is preserved.

- Restored public Ernie Aim 1 assets and the four published Aim 2 poses from Git deployment snapshot `04263d28d0cd3e4e549e5bd9bb57a7fee0e3a5c8`. Assets remain ignored; `scripts/restore_public_ernie.mjs` reproduces restoration.
- Subject switching immediately clears positional groups and invalidates pending analysis/PLY callbacks. The selected subject loads its own analysis; default scalp visibility is restored instead of inheriting the common-skin override.
- Positional reset removes old QC/render attributes, variant controls, export payload and mesh resources.
- `src/export_web.py` generates a public-only tracked registry and an ignored complete local registry. npm dev/build refresh both before Parcel starts. Existing individual-subject work remains available locally.
- Refreshed the already-staged public registry only, removing private-subject references from its pending contents. Other staged merge changes were preserved.
- Updated existing usage in `README.md` and `docs/efield.md`.

## Verified results

| Check | Result |
|---|---|
| Python suite, tms312 | 104 passed; socket test initially sandbox-blocked, then passed separately with loopback permission (105 tests total) |
| JavaScript unit suite, tms312 | 27 passed |
| Production Parcel build | Passed with writable LMDB cache permission |
| Chrome positional acceptance | Passed; local report/reload, then switch to MNI152, disabled positional controls, cleared metadata/variants, scalp restored |
| Chrome public Ernie Aim 2 | Passed; F4/SMA, MRI-guided/Cap from MRI, difference mode, then MNI152 empty-field state; no page errors |
| Chrome landmark visibility follow-up | Three relevant specs passed together; edited all four Ernie landmarks in an isolated test browser, verified saved edits survive reload, and checked actual canvas pixels change when electrodes/arcs are toggled before and after reload |
| Ernie manifest | Four poses; all referenced asset files present |
| Public deployment guard | Correctly rejects mixed local workspace containing non-public heads |
| Privacy checks | Private data and complete local registry ignored; no tracked files under viewer/src/data; public registry excludes private subject |
| Diff whitespace | Working and staged diffs pass `git diff --check` |

## Limits / remaining work

- Restored existing public simulation outputs; no FEM rerun or new anatomical validation.
- Local `viewer/dist` is a private build: it includes locally available subjects and stays ignored. Do not publish it manually. The existing `npm run deploy` guard refuses mixed private data.
- Data ignored by Git does not enter a normal PR. Do not force-add ignored data or the local registry. Existing branch history already contained a private subject identifier in the old registry; this change removes current references, not historical commits.
- Only the two relevant browser specs were run, not the entire browser suite.
- User requested committing the merged changes and both viewer repairs together, without pushing. No generated private artifacts are included.
