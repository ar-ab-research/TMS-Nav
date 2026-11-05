# Aim 1 positional comparison

## Installation and quick start

Use the existing Python environment (`numpy`, `pyvista`, `nibabel`, `pytest`) and viewer Node dependencies. From repository root:

```sh
python -m scripts.positional_demo
python -m scripts.prepare_positional
python compare_positions.py saves/brainsight/restore/r-02/comparison/manifest.pending.json --out saves/brainsight/restore/r-02/comparison/results
python run_viewer.py
```

The first command produces a synthetic 5 mm geometry example. The second inventories the supplied r-02 project/image, creates local `exports/`, `comparison/`, `validation/` folders, and writes a **pending** manifest. Originals remain in place. Complete the manifest before the third command: it intentionally rejects unresolved inputs. No individualized result is possible until targets, mappings and coordinate/trajectory evidence are supplied. Do not treat the synthetic targets as MNI or individualized locations.

## Import support

`src.positional.read_targets(entry, context, export=None)` uses `.bsproj` as intended entry. Direct binary extraction and direct network project retrieval are **unavailable**. Pass an independent planned-target text export with the project entry. This mode is explicitly recorded as `target-text-export-fallback`. Text format versions 12 and 14 are accepted, with explicit millimetre units and NIfTI:Aligned or NIfTI:Q:* frames matching reviewed context. Other formats fail closed. Targets retain names, original columns, orientation matrix, header/source/version/hash and export positions; Samples are excluded and counted. Orientation remains in export axes and is never interpreted as a planned trajectory automatically.

Sources investigated:

- [Rogue downloads and current manuals](https://www.rogue-research.com/downloads/).
- [Official 2.5.6 release](https://www.rogue-research.com/fr/2025/02/brainsight-2-5-6-released/): TCP server and vendor-provided protocol/Python examples; macOS 10.14 minimum, 10.15 for full network functionality.
- [NIBS manual chapter 18](https://www.rogue-research.com/wp-content/uploads/Brainsight-NIBS-2.5.11.pdf): request/response or streaming; examples available from vendor. No public complete command schema was obtained in this investigation. Opening a project, retrieving all planned targets/trajectories, coordinate metadata and anatomical references remain unverified capabilities. No endpoints are invented. Obtain the version-matched protocol and examples from Rogue Research before implementing transport. Release notes also describe a coordinate-system response bug fixed in 2.5.8: do not trust earlier network responses without independent validation.
- [SimNIBS documented export workflow](https://simnibs.github.io/simnibs/build/html/documentation/neuronavigation/brainsight.html): planned Targets and recorded Samples differ. Export NIfTI:Aligned for Brainsight ≤2.5.2, NIfTI:Q:xxx for ≥2.5.3, using the same individual anatomical NIfTI.

## Manifest and coordinate contract

Use generated manifest paths relative to its directory. Supply the full-resolution native scalp VTP, its SHA256, and review evidence; never use skull or a display-decimated surface for measurement. Saved marker JSON must identify the marker MRI via `source_sha256`. Use original `fiducials` positions, with exact unique names. Explicitly assign SMA and right_DLPFC to marker names and planned target names; right_DLPFC is paired with cap F4. There is no SMA=Cz rule and no ordering inference. Review the physical marker-to-cap label relationship yourself.

`context` requires exact `coordinate_system`, `source_mri_sha256`, `marker_mri_sha256`, and `frame_evidence` describing verification in Brainsight and the NIfTI header. CLI loads both MRI headers using existing strict native loader: explicit spatial units, coded qform/sform, reject conflicting forms, template codes or sheared grids. Q coordinates must match the reviewed anatomical world frame. Different MRI hashes require `registration` with `verified:true`, `evidence`, matching `source_sha256`/`target_sha256`, and `matrix`: source RAS mm → marker RAS mm. This is registration evidence, not just a numerical inverse check.

API `normalize` separately supports voxel indices via explicit voxel-to-RAS-mm affine, LPS/RAS and mm/meters/microns. Export units are fixed to documented millimeters. Mesh, markers and normalized targets must all share marker MRI RAS mm. Neither MNI coordinates nor viewer camera rotations/scaling enter the distance formula.

`semantics` maps exact target names to either:

```json
{"outside":[0,0,100],"inside":[0,0,0],"verified":true,"evidence":"Documented planned segment, endpoints transformed into marker MRI RAS mm; direction verified in Brainsight"}
```

or `{"documented_scalp_point":true,"verified":true,"evidence":"Source documentation and independent anatomical verification"}`. Numbers above illustrate syntax only. Trajectory endpoints must be derived from documented project semantics, not guessed from matrix columns. They are supplied in the destination marker MRI frame. The segment must start outside, end inside a closed scalp and have one unique intersection. Open meshes, missing/reversed/ambiguous intersections are invalid. A documented scalp point must lie within 0.1 mm of the comparison mesh. Missing trajectory evidence keeps the raw target and disables the primary comparison; no exploratory substitution is performed.

## Measurements and viewer

`compare` projects raw cap points to closest **triangle points**, retaining projection distance and originals. Distance is `norm(eeg_scalp - brainsight_scalp)` in MRI-world mm. Each subject/target gets a QC status and exclusion reason. JSON and CSV include nested provenance and coordinates (nested CSV values are JSON). Summary uses one observation per subject/target, sample SD (undefined for n=1), median and linear-percentile IQR. Invalid pairs are excluded with reasons. No equivalence test or coil angles are calculated from markers.

In the existing HTML viewer select the matching subject, open **Aim 1 positional scalp comparison**, and load results JSON. MRI identity must match. Independent toggles control original cap markers, projected points, raw targets/trajectories, derived scalp points and comparison lines. The panel labels SMA/F4, methods, distances, QC and separate target summaries; buttons export JSON/CSV. Switching subjects clears overlays. Reload results after editing/reviewing markers; stale results must not be used for validation.

## Patient validation

1. Open the supplied `.bsproj` in licensed Brainsight on macOS; confirm anatomical image identity and version. Export **planned Targets**, with full coordinate and orientation columns, documented NIfTI coordinate settings, and maximum available decimal precision. Save under `exports/planned-targets.txt`; Samples never replace Targets.
2. Identify each marker and target explicitly. Verify scalp segmentation including defacing/caps/holes and marker artifacts. Record registration evidence if MRIs differ. Resolve qform/sform ambiguity before importing.
3. Verify target position semantics and inward trajectory in orthogonal anatomical views. Supply documented segment endpoints or scalp-contact evidence in the marker MRI frame. Check each computed scalp intersection visually.
4. Obtain a second independent export from the same project and compare with `--validate-export path --decimals 4` (use the actual lesser decimal precision). The report gives maximum Euclidean discrepancy, tolerance `sqrt(3)*10^-decimals` mm for two rounded exports, and pass/fail. Both exports must have identical unique target names and verified frames. For anisotropic registration scaling, propagate precision through the transform or compare in the original source frame; the simple tolerance assumes metric-preserving transforms.
5. Verify imported points against Brainsight crosshairs, known physical offsets, left/right and superior/inferior landmarks. Numerical agreement establishes import consistency only; it does not establish anatomical or registration accuracy. Record both separately. Retain exports and QC locally; never commit subject data.
