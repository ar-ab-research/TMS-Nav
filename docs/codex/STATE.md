# Codex state

Updated: 2026-11-05

## Current objective / completed
- User explicitly accepted current result after inspecting rendering/QC. Recorded exact-surface-hash-bound visual acceptance locally; GUI/export status now REVIEWED. Numerical result and all QC retained; independent clinical accuracy not implied.
- Replaced Brainsight pyramids with spheres positioned directly at target MRI-world coordinates (sphere center, no offsets).
- Removed legacy Aim 1 metrics/session-results subsection from right panel, retaining all newer positional, trajectory, surface, registration and review sections. Removed stale references in MRI review code.
- Updated usage/report with acceptance scope and cleanup.

## Verified
- Current focused Python suite 16 passed, JS 21 passed, actual Chrome acceptance/pixel toggles passed, final production build passed. Browser screenshot inspected: reviewed badge, centered spheres, legacy block absent, QC retained, no browser errors.
- Prior full suite 96 passed; not repeated for this focused cleanup.
- Raw positions/geometry/metric unchanged; local report regenerated. Acceptance file and subject artifacts ignored. No private coordinates/results in checkpoints.

## Decisions / remaining limits
- Acceptance scope is user visual QC, distinct from independent clinical/anatomical accuracy validation. Changed surface hashes still invalidate acceptance.
- Separate trajectory endpoint still requires its documented semantics; missing site remains absent.
- Use micromamba tms312. Prior external push rejection unresolved; no retry/bypass.

## Uncommitted changes / next actions
- Task changes delivered in [codex] commit; verify hash in Git. No unrelated changes present at task start.
- Refresh local viewer and Reload analysis. Independent patient/export validation remains separate.
