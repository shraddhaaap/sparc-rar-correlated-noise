#!/usr/bin/env python3
"""Print the headline numbers from the newest collected runs, next to the reference values from the earlier runs.

Usage:  python tools/headline_numbers.py            (after tools/collect_results.py)

It reads results/05_Results and reports:
  * nulls and power  (Notebook 08X merged run if present, else Notebook 08 v2):  family-wise rates, per-slope
    false-positive ranges, calibrated z beyond the Student-t cutoff, C2 calibrated power;
  * S3 slopes        (newest Notebook 09 run with S3 fits);
  * Model D          (newest 04/04L run: global R-hat if a diagnostics table is present).
Values that differ from the reference runs are marked  <-- CHANGED.
"""
from pathlib import Path
import pandas as pd

R = Path(__file__).resolve().parents[1] / "results" / "05_Results"
V4 = {  # reference values (runs 20261028T075632Z, 20261105T161628Z, 20261106T081353Z)
    "fw": {"A1_null_fitted": "15/15", "C1_null_shuffled": "14/14", "C3_null_constant": "12/12", "C4_null_fractional": "14/15"},
    "beyond_t": {"C1_null_shuffled": [], "C3_null_constant": ["log_sigma_int-logMbar", "log_sigma_int-logSB0", "log_sigma_int-fgas"],
                 "C4_null_fractional": ["beta-logMbar"]},
    "s3_supported": 0,
}

def newest(pattern):
    c = sorted(R.glob(pattern)); return c[-1] if c else None

def tables_dir(run): return run / "tables" if (run / "tables").is_dir() else run

def pick_runs():
    """Best run per mock-noise kernel: the 08X run with the most fits (normally the merged run); else Notebook 08 v2."""
    best = {}
    for run in sorted(R.glob("Injection_Recovery_08X/*")) + sorted(R.glob("Injection_Recovery_Extended/*")):
        f = tables_dir(run) / "08_mock_fit_results.csv"
        if not f.exists(): continue
        d = pd.read_csv(f, usecols=lambda c: c in ("mock_id", "fit_covariate", "noise_kernel"))
        kern = str(d.noise_kernel.dropna().iloc[0]) if "noise_kernel" in d and d.noise_kernel.notna().any() else "se"
        n = d.drop_duplicates(["mock_id", "fit_covariate"]).shape[0]
        is08x = run.parent.name == "Injection_Recovery_08X"
        key = (is08x, n)
        if kern not in best or key > best[kern][0]: best[kern] = (key, run)
    return {k: v[1] for k, v in best.items()}

def nulls_block():
    runs = pick_runs()
    if not runs: print("No Notebook 08/08X run collected."); return
    for kern, run in sorted(runs.items()):
        print(f"\n#### mock noise kernel: {kern}")
        one_null_block(run)

def one_null_block(run):
    t = tables_dir(run); print(f"\n== Nulls and power: {run.parent.name}/{run.name}")
    fwp, nup = t / "08_family_wise_rates.csv", t / "08_population_independent_nulls.csv"
    if not fwp.exists():
        print("  summary tables not found (only fit-level results): open the run's report, or re-run the notebook's report cells"); return
    fw = pd.read_csv(fwp)
    for r in fw.itertuples():
        val = f"{r.n_with_any_supported}/{r.n_mocks}"; old = V4["fw"].get(r.scenario)
        print(f"  family-wise {r.scenario:20s} {val:>7s}  [{r.fw_95_low:.2f}, {r.fw_95_high:.2f}]" + ("" if old == val else f"   <-- CHANGED (before: {old})"))
    nu = pd.read_csv(nup)
    for scen, g in nu.groupby("scenario"):
        rng = g.groupby("parameter").false_positive_rate.agg(["min", "max"]).round(2).to_dict("index")
        beyond = sorted(f"{a.parameter}-{a.covariate}" for a in g.itertuples() if a.beyond_t_cutoff)
        old = V4["beyond_t"].get(scen)
        print(f"  {scen}: n per slope {g.n_mocks.min()}-{g.n_mocks.max()}; FP ranges {rng}")
        print(f"      beyond t-cutoff: {beyond or 'none'}" + ("" if old is None or sorted(old) == beyond else f"   <-- CHANGED (before: {old or 'none'})"))
    pw = t / "08_C2_power_by_parameter.csv"
    if pw.exists(): print("  C2 power by parameter:\n" + pd.read_csv(pw).round(2).to_string(index=False))

def s3_block():
    runs = [r for r in sorted(R.glob("Sensitivity/*")) if (tables_dir(r) / "09_S3_slopes_inside_fixed_gp.csv").exists()]
    if not runs: print("\nNo Notebook 09 S3 table collected."); return
    run = runs[-1]; s3 = pd.read_csv(tables_dir(run) / "09_S3_slopes_inside_fixed_gp.csv")
    s3 = s3[s3.parameter != "-"]; n_sup = int(s3.supported.sum())
    print(f"\n== S3 slopes inside the correlated-noise model: Sensitivity/{run.name}")
    print(f"  supported: {n_sup}/{len(s3)}" + ("" if n_sup == V4["s3_supported"] else f"   <-- CHANGED (before: {V4['s3_supported']})"))
    print(s3[["parameter", "covariate", "slope_median", "slope_sd", "z", "max_rhat_global"]].round(3).to_string(index=False))

def modelD_block():
    run = newest("Diagnostics/04_GP_Debugged/*")
    if run is None: print("\nNo Model D run collected."); return
    print(f"\n== Model D: 04_GP_Debugged/{run.name}")
    for f in sorted(run.rglob("*convergence*.csv")) + sorted(run.rglob("*full_model_D*diagnostics*.csv")):
        print(f"  {f.relative_to(run)}"); d = pd.read_csv(f); print(d.head(12).to_string(index=False)[:2000])
    print("  Reference run 20261026T083032Z: tau R-hat 1.029 (ESS 262), one divergence, four galaxies failing.")

if __name__ == "__main__":
    nulls_block(); s3_block(); modelD_block()
