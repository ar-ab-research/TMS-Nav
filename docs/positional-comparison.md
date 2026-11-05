# Run the positional analysis

From the repository root, using the existing `tms312` environment:

```sh
export PATH="$HOME/micromamba/envs/tms312/bin:$PATH"
python compare_positions.py --subject r-02
python run_viewer.py
```

Open **http://127.0.0.1:1234**, select **r-02**, and scroll down the **right sidebar** to **Aim 1 positional scalp comparison**. Results load automatically. After rerunning analysis, click **Reload analysis**. No manual JSON import is needed.

Output files:

- `saves/derivatives/subjects/r-02/positional.json`
- `saves/derivatives/subjects/r-02/positional.csv`

The command works with the files currently supplied: it projects the four saved cap markers onto the full scalp mesh and renders those real points. **SMA/F4 distances are currently unavailable**, for the specific reasons below. The report shows these reasons instead of inventing measurements.

## What the supplied files still need

| Item | Current finding | Required action |
|---|---|---|
| Planned target coordinates | `.bsproj` is present; its coordinates are undocumented binary objects. Brainsight is not installed here. | In Brainsight, export planned **Targets** to `saves/brainsight/restore/r-02/exports/planned-targets.txt`. Choose **NIfTI:Q:xxx** for Brainsight ≥2.5.3, **NIfTI:Aligned** for older versions. Include position, orientation and maximum decimal precision. |
| Marker mapping | Four saved points are named `manual-1` through `manual-4`, without anatomical labels. | Identify the SMA marker and F4 marker explicitly. No marker-order or SMA=Cz inference. |
| Right DLPFC | Project inventory lists SMA and SMA Skin, with no explicitly named right-DLPFC/F4 target. | Supply that planned target, or identify its exact name in a corrected project/export. |
| MRI registration | Project anatomy differs from the MRI used for the saved cap markers. | Supply/review a source-to-marker MRI registration in RAS millimeters. Header coordinates alone do not prove alignment. |
| Scalp entry | Planned-point/trajectory meaning is not verified. | Confirm the documented scalp point or an inward segment crossing scalp once. |

## When those inputs are available

Complete the existing local `saves/brainsight/restore/r-02/comparison/manifest.pending.json`, then save it as **manifest.json** in the same folder. The same `--subject r-02` command will then run the full comparison and save results to the same viewer location.

The manifest requires:

- Exact project/export, marker MRI, source MRI, saved marker JSON and **full-resolution scalp** paths; paths are relative to the manifest. Use SHA256 identities for both MRIs and scalp.
- Explicit `mappings.SMA` and `mappings.right_DLPFC`, each with exact `marker` and `brainsight` names. The latter is the cap **F4** comparison.
- `context.coordinate_system` matching the export, both MRI hashes, and `frame_evidence`. Different MRIs additionally need `context.registration`: `verified: true`, `evidence`, matching `source_sha256`/`target_sha256`, and a 4×4 `matrix` mapping source RAS mm to marker RAS mm.
- Reviewed scalp evidence and `semantics` keyed by exact target name. Either a verified documented scalp point, or verified `outside`/`inside` trajectory endpoints **already in marker MRI RAS mm**, with evidence. Do not derive an axis from undocumented matrix columns.

The lower-level command is also available:

```sh
python compare_positions.py path/to/manifest.json --out saves/derivatives/subjects/r-02/positional
```

## Viewer and interpretation

Five independent toggles show raw cap points, projected cap points, raw Brainsight targets/trajectories, Brainsight scalp points, and comparison lines. Tables show each target's separation and cap projection offset in millimeters. Export buttons save JSON/CSV, including provenance and QC. Marker or subject changes require rerunning analysis; mismatched saved marker coordinates are rejected.

The gray surface is **scalp**, not skull. Cap projection uses triangle interiors, not nearest vertices. Primary distance is `||cap_scalp − Brainsight_scalp||₂` in native MRI-world mm, independent of camera/display transforms. Unverified pairs are excluded from summaries. Each target has its own n, mean, sample SD, median and IQR; no equivalence or coil-angle claim follows from these points.

## Validate before interpreting patient results

1. Check target/marker labels, left/right, scalp segmentation, trajectory entry and registration in anatomical views.
2. Obtain a second independent export from the same project. With the actual export precision (example: four decimals):

   ```sh
   python compare_positions.py --subject r-02 --validate-export path/to/independent.txt --decimals 4
   ```

   The report prints maximum coordinate discrepancy and a rounding tolerance of `sqrt(3) × 10^-decimals` mm. This assumes metric-preserving registration; compare in source coordinates or propagate precision for scaled transforms.
3. Record numerical agreement separately from anatomical/registration accuracy. No patient validation is claimed yet.

## Support boundaries and references

Python dependencies: existing `numpy`, `pyvista`, `nibabel`; viewer: Node/npm and `npm ci` in `viewer/`. Adapter API: `src.positional.read_targets(project, context, export=...)`; text format versions **12/14**, explicit millimeters, documented NIfTI frames. Planned Targets remain separate from recorded Samples. Raw names, source/version, orientation and provenance are preserved. Unknown frames, conflicting coded qform/sform, invalid units and missing registration are rejected.

Direct `.bsproj` coordinate extraction/network retrieval is unavailable. The read-only SQLite inventory reads names only; it never decodes coordinate blobs. Rogue Research documents a TCP interface and vendor-provided examples, but the complete project-opening/retrieval protocol was not obtained. Request version-matched protocol/examples before extending direct support; no endpoints are guessed.

References: [Rogue downloads/manuals](https://www.rogue-research.com/downloads/), [official network announcement](https://www.rogue-research.com/fr/2025/02/brainsight-2-5-6-released/), [documented SimNIBS export settings](https://simnibs.github.io/simnibs/build/html/documentation/neuronavigation/brainsight.html).
