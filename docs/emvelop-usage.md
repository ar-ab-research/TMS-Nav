# EMvelop / two-loop feasibility usage

Run from the repository root:

```bash
micromamba run -n tms312 python scripts/run_emvelop.py
micromamba run -n tms312 python -m pytest tests/test_emvelop_feasibility.py -q
```

- Outputs: `analysis/emvelop/results.json` (all 181 candidate phases except target nulls, three grid resolutions), `analysis/emvelop/fields.png`.
- Change output directory with `--output PATH`.
- Configure geometry, sinusoidal frequency/current, conductivity, duty and illustrative pointwise SAR budget through `Config` in `src/emvelop_feasibility.py`; import `run(config, step)` for parameter studies.
- This module is independent of patient data and the existing navigation/forward pipeline. NumPy and Matplotlib are already available in `tms312`.

## Model and conventions

- Two 5 cm radius single-turn loops lie in yz planes at x = ±10 cm, both wound about +x. Region of interest is a 9 cm radius sphere. Target is (0, 3 cm, 0); center is an exact axial electric-field null.
- Numerically integrate A/I = μ₀/(4π) ∮dl/r, then E = −∂A/∂t. A common phasor −i is omitted from norm calculations. No scalar-potential boundary correction, anatomy, tissue wave propagation or neural response is solved.
- Peak current 5 kA per loop, 3 kHz. The same-frequency sweep uses relative phase 0–180°; remaining phases are redundant for real primary-field bases. Both amplitudes are fixed equal. At each phase, focality is the total volume with |E| ≥ half the target value, including disconnected/off-target regions. Minimize this volume with nonzero target; break ties by target/global-maximum ratio. Uniform rescaling to a fixed target field leaves this metric unchanged. A zero-field solution cannot win.
- The equivalent sphere diameter is derived from that total volume. It is **not FWHM along a line**, not a connected focus diameter, and not directly comparable to a paper's differently defined focality.
- Coaxial-loop E fields are parallel at every point. For nearby distinct carrier frequencies, envelope depth is therefore 2 min(|E₁|, |E₂|); the tiny frequency offset is neglected in field amplitudes. Relative phase only shifts beat timing, not its spatial envelope. TI heating is the sum of carrier mean squares after averaging complete beats.
- Peak-phasor tissue heating proxy: SAR = σ|E|² D/(2ρ). σ = 0.2 S/m, ρ = 1000 kg/m³. D = 0.002 represents an assumed sinusoidal-equivalent 200 μs burst repeated at 10 Hz; it is not an exact clinical pulse waveform. Continuous TI uses D = 1. Real pulse comparison requires integrating E(t)².
- `sar_budget = 2 W/kg` is an illustrative **pointwise** time-average constraint, not a regulatory spatial/time-averaged limit or proof of safety. Scaling to that budget ignores coil copper heating, drive voltage, energy recovery, nerve stimulation and all hardware limits. Conductivity is passive postprocessing on a vacuum solution, not a conducting-head forward solution. No temperature PDE is solved.

## Verification and interpretation

- Tests check axis null, mirror symmetry, opposing-current cancellation, segment quadrature convergence, current linearity and peak/RMS/duty factors.
- Default run compares 6, 4 and 3 mm grids. Half-target volumes change by <0.3% from 4 to 3 mm. Maximum SAR changes by ~3.7% (same carrier) and ~3.4% (TI): surface hotspot estimates remain discretization-limited.
- Rotational symmetry around x makes an isolated off-axis point focus impossible with this geometry; fields form rings. Phase control cannot repair the axial null. The published GHz model is a literature comparator, not reproduced by this script.

- Results additionally provide `sqrt_half_target_area_cm` on the exact z=0 disk (square root of total half-target area), maximum field, and single-turn current needed for 12/100 V/m. The optimized objective remains total 3D volume; this 2D diagnostic permits a closer metric comparison but does not reproduce anatomical RF modeling.
- Complex vector norm here equals peak amplitude because coaxial-loop basis vectors are collinear at every observation point. For nonparallel coil fields it would instead represent the square root of twice the cycle-mean |E|², and must not be labeled instantaneous peak without solving the polarization ellipse.
- Exported heating arithmetic examples compare balanced continuous RF envelope 12 V/m at σ=1 S/m (each carrier peak 6 V/m) against single-carrier low-frequency peak amplitudes at configured σ and duty. These are local heating examples, not equivalent neural doses or matched spatial distributions.
