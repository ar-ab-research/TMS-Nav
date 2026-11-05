# Aim 1 usage

Use **micromamba tms312** from the repository root.

## Save the confirmed SMA pairing

```sh
micromamba run -n tms312 python compare_positions.py --subject r-02 --confirm-sma-marker manual-1
```

This explicitly saves **manual-1 → Brainsight SMA** in local `saves/brainsight/restore/r-02/comparison/review.json`, with MRI identities and confirmation evidence. It does not move markers or select SMA Skin. This pairing is already saved for the supplied case. No proximity inference is used.

Later runs reuse that pairing:

```sh
micromamba run -n tms312 python compare_positions.py --subject r-02
micromamba run -n tms312 python run_viewer.py
```

Open **http://127.0.0.1:1234**, select **r-02**, and click **Reload analysis**.

## Two separate endpoints

| Endpoint | Definition | Gates |
|---|---|---|
| **SMA scalp-projected localization difference (mm)** | Euclidean distance between independent closest triangle-interior points for confirmed cap SMA and exact Brainsight SMA on one common skin mesh | Known frames/units, confirmed pairing, registration QC, surface identity/quality. No trajectory/contact requirement. |
| Scalp-entry localization difference (mm) | Projected cap point versus documented scalp contact or valid inward trajectory intersection | Separate mapping/registration/entry-semantics gates. No nearest-point substitute. |

The projection result is single-subject, not a cohort statistic or cortical targeting error. **Unreviewed surface or alignment produces a visibly PROVISIONAL preview**, not a verified measurement. Unresolved frames, failed numerical registration or absent mapping cannot produce a number. SMA Skin is a separate diagnostic variant; F4 remains missing.

## Common skin and QC

The original cap mesh is a processed head mask; it is not certified skin-only. The scan contains external fiducials and acquisition artifacts. A registered, apparently cap-free anatomical image provides an alternative candidate. Candidate reconstruction uses an air/tissue threshold, largest connected tissue component, enclosed image-plane hole filling to suppress internal interfaces, and unsmoothed marching-cubes contour. It does **not** erode, offset, or cosmetically smooth the boundary. This is still provisional: T1 skin/hair ambiguity, segmentation irregularities and FOV-truncated edges require anatomical review.

The CLI rebuilds all projections on the selected full-resolution candidate. Full source MRI hash, transform and algorithm version identify its cache. Surface review must match the exact mesh hash. Raw markers/targets stay unchanged. Display decimation is separate from measurement geometry.

Inspect **Common skin QC** and **Registration QC** in the sidebar. Local artifacts under `saves/derivatives/subjects/r-02/`:

- `common-skin/skin-qc.png`: cap/source slices through confirmed SMA marker and target, old mask orange and candidate green. Off-plane point offsets are labeled.
- `common-skin/skin-qc-manual-*.png`: other fiducial regions for bump/artifact inspection.
- `common-skin/common-skin.vtp`: full measurement mesh; `.ply`: display mesh.
- `common-skin/audit.json`: original/selected projection discrepancy, competing regions and independent nearest-triangle checks.
- `brainsight/registration/registration-qc.png`, `registration.json`, `cap_to_source_LPS.tfm`, `source_in_cap.nii.gz`: alignment QC/provenance.

Use **Original cap surface (QC)** and **Common skin candidate** toggles for before/after mesh inspection. Do not mark the candidate verified just to clear the provisional badge. After anatomical review, a local `common-skin/surface-review.json` must contain the exact `surface_sha256`, `verified: true`, and detailed `evidence`; changed geometry invalidates that review. Registration has its own reviewed/hash-bound status.

## Viewer controls

Expand **Brainsight layers**: parent show/hide, surface/raw-target controls, then independent persistent **SMA** and **SMA Skin** enabled/raw/projected checkboxes. The projection layer controls both methods' translucent red/green dots. **Raw → projection lines** adds labeled lines. **Comparison lines** shows the separately labeled endpoint connection. Original fiducials are red diamonds; targets green pyramids. Current single-subject projection value, raw/source/cap coordinates, projected coordinates and offsets appear in the right panel; trajectory results remain separate below.

## Exports and validation

- `positional.json`: both endpoints, full coordinates, confirmation, registration, selected surface and discrepancy audit.
- `positional-projection.csv`: one flat projection-result row, with nested provenance serialized as JSON.
- `positional.csv`: legacy trajectory rows; viewer CSV export includes both endpoint types.

Rigid registration uses cap as fixed and source as moving. SimpleITK's fixed-to-moving LPS resampling transform is inverted and conjugated by the RAS/LPS flip to obtain source-RAS → cap-RAS mm. No viewer offsets enter measurement. Audit verifies rigid separation preservation, exactly-once transforms, names/units, full-mesh identities, independent exhaustive triangle projection and display-mesh offsets. Registration image agreement, numerical agreement and anatomical accuracy are distinct.

Independent same-project export comparison remains available via the reviewed-manifest command with `--validate-export independent.txt --decimals 4`; use actual precision. Text formats 12/14 and validated NIfTI frames are supported; planned Targets and recorded Samples remain separate. Direct undocumented project-coordinate decoding is unsupported.

References: [Rogue manuals](https://www.rogue-research.com/downloads/), [Scanner naming](https://www.rogue-research.com/blog/page/3/), [SimNIBS export guidance](https://simnibs.github.io/simnibs/build/html/documentation/neuronavigation/brainsight.html).
