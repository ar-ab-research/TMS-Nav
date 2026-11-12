# Codex state

Updated: 2026-11-12

## Objective / completed
- Extended EMvelop reproduction attempt and two-coil TMS design; rewrote comparison report with explicit LaTeX forward/optimization equations, standalone equation diagram and multiple field/phase/thermal figures.
- Added homogeneous full-wave dyadic finite-line RF operator, 12 antennas/array, constrained complex nonconvex MFT optimization; new TMS offset/tilt geometry and amplitude/phase search; shared conservative steady Pennes solver.
- Corrected source interpretation: original 3D metric cube-root volume; MFT objective minimum carrier power, not sum. Original baseline kept for continuity.

## Verified
- Combined focused physics suite 15 passed (including Maxwell residual/asymptote, complex gradients, quadrature, nullspace constraints, heat conservation).
- RF 3mm L50 3.613/2.824cm, approximate SAR-scaled intensities37.70/5.73V/m: not exact original anatomical reproduction. 4mm reoptimization changes MFT focality .040%, intensity .99%.
- TMS central target reachable with offsets; L50 10.932cm, target2.357V/m at5kA/coil cap.
- Shared 1K steady thermal ceiling targets36.98/5.40/1228.98V/m (RF baseline/MFT/TMS), thermal-only extrapolations excluding hardware/neural limits. Temperature solve residuals<1e-10.
- Generated and inspected figures; all Python in micromamba tms312. No private data or existing subject workflow changed.

## Assumptions / blockers
- Original anatomy/COMSOL/antenna mesh/material table/optimized currents unavailable. RF homogeneous method reconstruction only; no tuning to published numbers. Approximate9.261g averaging not exact10g compliance.
- Source retrieval: indexed original abstract/author page/patent available; direct thesis download failed. Reports distinguish sources and independent model.
- Local optimization not guaranteed global; shared thermal coefficients illustrative. Exact reproduction requires original data/specification.

## Git / next actions
- Prior implementation3b8af2d/checkpointc8cb4a2 pushed. Current extension pending commit/push; outcome in final handoff.
- Next research step: original anatomical transfer matrices or complete reconstruction inputs, finite-duration thermal and hardware-constrained design; do not present thermal-only extrapolation as feasible current prescription.
