# Aim 1: registered scalp-entry comparison

Always use **micromamba tms312**. From the repository root:

```sh
micromamba run -n tms312 python compare_positions.py --subject r-02
micromamba run -n tms312 python run_viewer.py
```

Open **http://127.0.0.1:1234**, select **r-02**, and click **Reload analysis**. The first run registers the MRIs; later runs use a hash-bound cache.

## Display and measurements

Brainsight scalp and raw targets overlay the cap MRI in **cap MRI RAS world millimeters**, with no viewer offsets. The cap scalp is the common measurement surface. Use the existing left **LAYERS** panel: MRI fiducials (red diamonds), Brainsight targets (green pyramids), Brainsight MRI surface (lavender scalp), one **Scalp projections** toggle (translucent red/green dots for both methods), verified entries and comparison lines. Choices persist across reloads. The latter is a translucent display overlay only.

**Imported Brainsight targets** shows **scalp-entry localization difference (mm)** for valid confirmed pairs, or **Unavailable**. This is not cortical targeting error. Raw-target offsets to scalp and the new Brainsight closest-triangle projections are **exploratory/QC only**, never substitute entry points. The registered extracted surface is scalp, not a cortical brain mesh.

The supplied export contains SMA and SMA Skin, automatically assigned to internal SMA with variants preserved. F4/right DLPFC is absent. “SMA Skin” is approximately 30.5 mm off the common scalp after registration. Its name does not verify scalp contact. Export columns contain position/orientation but no documented scalp-entry designation or unambiguous inward planned segment. Primary distances also require confirmed cap-marker identities; proximity/order do not establish identity.

## Registration QC

Rigid, six-degree-of-freedom registration uses SimpleITK Mattes mutual information, seed 1729, one thread, 4/2/1 resolution levels. Cap MRI is fixed; source MRI is moving. SimpleITK's resampling transform maps **cap LPS → source LPS**. Invert and conjugate by the RAS/LPS flip to obtain **source RAS → cap RAS** for points/surfaces/verified segment endpoints. Rotate orientation columns without inventing trajectory meaning.

Expand **Registration QC** in the sidebar. Local files under `saves/derivatives/subjects/r-02/brainsight/registration/`:

| File | Meaning |
|---|---|
| `registration.json` | MRI hashes, source-to-cap RAS matrix/inverse, numerical checks and anatomical-review evidence |
| `cap_to_source_LPS.tfm` | Fixed-to-moving resampling transform |
| `source_in_cap.nii.gz` | Registered source image on cap grid |
| `registration-qc.png` | Nine orthogonal before/after overlays: cap magenta, source green |

Inspect ventricles, brain outline, midline, scalp and defacing differences. The local registration passed numerical and agent visual technical review; independent patient accuracy remains unvalidated. New registrations default to `verified: false`: estimated overlays are labeled and cannot yield primary measurements until reviewed. Numerical invertibility alone does not establish alignment.

## Confirming a measurement

The CLI creates `saves/brainsight/restore/r-02/comparison/review-template.json`. Complete it and save as **review.json**:

1. Retain matching source/marker MRI hashes.
2. For each available site, set exact `marker`/`brainsight` names, `confirmed: true`, and confirmation `evidence`. Do not replace a missing target with another site's target.
3. Supply selected-target `semantics`: explicit `frame` (`source_MRI_RAS_mm` or `cap_MRI_RAS_mm`), `verified: true`, documentation `evidence`, and either `documented_scalp_point: true` or documented inward `outside`/`inside` xyz endpoints. An orientation matrix alone is insufficient.
4. Inspect registration QC. Only then record `verified: true` and `evidence` in the hash-bound registration JSON. Changed inputs reset the gate.
5. Rerun the same CLI command and Reload analysis.

Documented scalp points must be within 0.1 mm of the common mesh or are rejected. Trajectories must start outside, end inside a closed scalp and intersect once; missing/reversed/ambiguous intersections are rejected. Cap projections use closest triangle interiors, retaining originals and projection offsets. Brainsight nearest-point substitution is prohibited.

## Outputs and validation

`positional.json`/`.csv` in `saves/derivatives/subjects/r-02/` retain raw/transformed coordinates, confirmed mappings, registration/semantic evidence, methods, QC/exclusions and measurement label. Valid pairs include `scalp_entry_localization_difference_mm`; `distance_mm` remains compatible with existing summaries. Each target separately reports n, mean, sample SD, median and IQR, excluding invalid pairs. Viewer Export buttons provide the report.

An independent same-project export can be compared through the reviewed-manifest API:

```sh
micromamba run -n tms312 python compare_positions.py path/to/manifest.json --out results --validate-export independent.txt --decimals 4
```

Use actual export precision. Maximum discrepancy is compared with `sqrt(3) × 10^-decimals` mm for rigid transforms. Numerical import agreement and anatomical/registration accuracy are distinct.

API modules: `src.positional`, `src.brainsight_registration`, `src.positional_subject`. Text versions 12/14, explicit millimeters and validated NIfTI frames (including header-gated legacy Scanner) are supported. Targets remain separate from Samples. Unknown frames/units, conflicting qform/sform and stale MRI identities fail closed. Direct `.bsproj` binary coordinate extraction remains unsupported.

References: [Rogue manuals](https://www.rogue-research.com/downloads/), [legacy Scanner rename](https://www.rogue-research.com/blog/page/3/), [SimNIBS export guidance](https://simnibs.github.io/simnibs/build/html/documentation/neuronavigation/brainsight.html).
