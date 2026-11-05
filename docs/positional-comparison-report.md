# Aim 1 projection endpoint and surface audit

## Implemented and confirmed

- User-confirmed pairing saved locally: **manual-1 → exact Brainsight SMA**. SMA Skin remains diagnostic; raw marker/target coordinates unchanged.
- Added **SMA scalp-projected localization difference (mm)**, independent of trajectory/contact semantics. Retained separate trajectory endpoint.
- Rebuilt all cap/target projections on one candidate full-resolution common mesh. Unreviewed surface keeps the numerical preview explicitly **PROVISIONAL**; it is not a verified anatomical measurement.
- Expandable persistent parent/variant controls for SMA and SMA Skin, their raw/projected points, labeled projection lines and optional endpoint line. Old/candidate meshes available for QC. Marker edits invalidate displayed results.

## Single-subject projection preview

**11.502175 mm — PROVISIONAL.** No cohort inference or cortical targeting-error claim.

| Coordinate | x | y | z |
|---|---:|---:|---:|
| EEG raw, cap RAS mm | -2.651125 | 13.250063 | 62.047623 |
| SMA raw, source RAS mm | 3.759900 | 8.190800 | 42.772300 |
| SMA raw, cap RAS mm | -1.476230 | 2.626337 | 22.131144 |
| EEG projected, cap RAS mm | -2.274959 | 13.039908 | 50.513903 |
| SMA projected, cap RAS mm | 1.596749 | 2.286589 | 49.219282 |

Projection offsets: EEG **11.541765 mm**, SMA **27.264003 mm**. Full coordinates/provenance are exported locally in JSON and projection CSV.

## SMA versus SMA Skin discrepancy

| Quantity | mm |
|---|---:|
| Raw separation, source | 1.877317110 |
| Raw separation, registered cap | 1.877317110 |
| Rigid preservation error | ~1.0e-14 |
| Projected separation, original cap mesh | 6.695386 |
| Original projection offsets: SMA / SMA Skin | 28.681984 / 30.505432 |
| Projected separation, selected candidate | 0.000000 |
| Selected projection offsets: SMA / SMA Skin | 27.264003 / 29.138018 |

Independent exhaustive NumPy triangle-interior/edge calculation agrees with VTK: original-mesh position discrepancy ≤1.4e-8 mm; candidate target and EEG discrepancies 0 mm at reported precision. Exactly-once source-to-cap transforms agree, raw separation is preserved, names/units are correct, and no display offsets are used. Candidate full-resolution projections differ from the display-decimated surface by up to **0.522 mm**; that does not explain the original 6.7 mm separation.

Original-mesh competing regions at least 5 mm apart are only **0.002203 mm** (SMA) and **0.047873 mm** (SMA Skin) farther than each global minimum. Closely spaced interior points can therefore switch nearest regions. The selected unsmoothed candidate maps both variants to the same corner/vertex; competing-region distance gaps are **0.282551/0.209761 mm**. This is geometrically permissible but sensitive to surface geometry/discretization. No target swap, double transform, VTK locator or viewer-world conversion bug was found. The original mask's anatomical interpretation and projection stability are the concern, not rigid-distance preservation.

## Surface evidence and unresolved validation

The existing cap mesh comes from a tissue/head mask with large-scale closing and smoothing, not explicit skin/fiducial/cap/hair separation. Anatomical slices show external marker signal and acquisition-dependent boundaries. It cannot be certified as pure skin by renaming it.

Assessed the registered apparently cap-free anatomical image as an alternative. Selected candidate: image-supported tissue threshold, largest component, enclosed-plane hole filling, unsmoothed contour, no erosion/cosmetic boundary displacement. A first naive threshold candidate retained internal tissue interfaces and was rejected; the revised candidate suppresses them. Registration and boundary overlays were inspected at the SMA marker/target and other fiducials.

The cranial region follows the visible outer tissue signal, but skin/hair ambiguity, local irregularities and **4040 FOV-related open edges** remain. The candidate is **not anatomically verified**. It is a defensible preview, not a completed skin reconstruction. The precise blocker to a verified endpoint is anatomical approval/correction of this skin-only surface (or a supplied reviewed skin segmentation), tied to the mesh hash. Independent patient registration accuracy also remains unvalidated.

QC artifacts (ignored locally): `common-skin/skin-qc.png`, per-fiducial slice overlays, full/display before-after meshes, `common-skin/audit.json`, and registration QC. Trajectory endpoint still lacks documented entry semantics; F4 target remains absent.

## Tests

Full Python suite: **96 passed**; focused projection/geometry suite: **16 passed**. Chrome acceptance passed for provisional result rendering, selected-skin display, parent/variant persistence, toggles, reload and export. Production build passed. Final focused projection/API suite: **17 passed**; JS: **21 passed**. All detected open-edge vertices were checked against source voxel bounds and lie at the FOV boundary.
