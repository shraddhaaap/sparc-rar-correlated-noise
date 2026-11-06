# Correlated rotation-curve noise and RAR population trends (SPARC)

Analysis notebooks and results by S. Patil, S. Patkar and A. Aylani (2026).

Tests of whether the radial acceleration relation (RAR) is universal usually treat the points of a rotation curve as independent. This project fits 153 SPARC galaxies (3,164 points) with a hierarchical Bayesian model that samples each galaxy's distance, inclination and mass-to-light ratio, separates galaxy offsets ($\tau$) from within-galaxy scatter ($\sigma_\mathrm{int}$) and models correlated residuals as a Gaussian process. Twelve pre-specified population slopes are tested against universal-RAR mocks with correlated noise, an injection test of power and three sensitivity analyses.

**Main result.** With independent errors, 8 of 12 slopes are formally significant, yet universal-RAR mocks with correlated noise (fitted, shuffled, constant or fractional amplitude) show at least one significant slope in 93–100% of cases. No slope passes against every plausible null, and none survives inside a correlated-noise likelihood.

## Repository layout

```
notebooks/            analysis notebooks, in pipeline order (archive/ = superseded versions, kept for provenance)
results/              small result files of every run, mirroring Drive's 05_Results/ (see results/RUNS.md)
tools/                collect_results.py (copy runs from Drive into results/), headline_numbers.py (headline numbers from the newest runs)
```

## Pipeline

| # | Notebook | Runs on | Output folder in `05_Results/` | Status |
|---|---|---|---|---|
| 01 | `01_Data_Audit` | Colab CPU | `Tables/`, `03_Processed_Data/` | done |
| 01B | `01B_External_Baryonic_Data_Audit` | Colab CPU | `Tables/` | done (no usable external decompositions) |
| 02 | `02_RAR_Baseline` | Colab CPU | `Tables/`, `Figures/` | done |
| 03 | `03_Hierarchical_Bayesian_Model` (Models A–C) | Colab CPU | `Posterior_Samples/`, `Diagnostics/` | done, run `20261022T095735Z` |
| 04 | `04_GP_Correlated_Errors_Debugged_Kaggle` (Models D, E) | Kaggle CPU | `Diagnostics/04_GP_Debugged/<run>/` | done, run `20261026T083032Z` (provisional) |
| 04E | `04E_Full_Model_E_Rerun_Kaggle` | Kaggle CPU | `Diagnostics/04_GP_Debugged/<run>/` | done |
| 05 | `05_Population_Dependence` | Colab CPU | `Population_Dependence/<run>/` | done, run `20261027T161151Z` |
| 06 | `06_Injection_Recovery` (nulls A1, A2) | Colab CPU | `Injection_Recovery/<run>/` | done, run `20261028T075632Z` |
| 07 | `07_Functional_Form_and_Cross_Validation` | Colab CPU | (see notebook) | done |
| 08 | `08_Population_Independent_Nulls_and_Recovery_v2` (C1, C3, C4, C2) | Colab CPU | `Injection_Recovery_Extended/<run>/` | done, run `20261105T161628Z` |
| 09 | `09_Real_Data_Sensitivity_v3` (S1, S2, S3) | Colab CPU + T4 GPU for S3 | `Sensitivity/<run>/` | done, run `20261106T081353Z` |
| **04L** | `04L_Model_D_Long_All_Galaxies_Kaggle` | Kaggle CPU, ≈ 8 h | `Diagnostics/04_GP_Debugged/<run>/` | **pending** |
| 04L | `04L_Model_D_Long_Without_4_Galaxies_Kaggle` (optional check) | Kaggle CPU | same | optional |
| **08X** | `08X_Extended_Nulls_Power_Kernel` | Colab/Kaggle CPU, split into sessions | `Injection_Recovery_08X/<run>/` | **pending** |
| **09 v4** | `09_Real_Data_Sensitivity_v4` (S3 refit) | Colab T4 GPU, ≈ 4 h | `Sensitivity/<run>/` | **pending** |

Every notebook writes into a **new, timestamped run folder** and never overwrites earlier output, writes an integrity-check register, stops on any failed critical check, and can resume an interrupted run with `RAR_RESUME_FROM`.

## Running the pending notebooks and merging the results

The order matters, because each step uses the previous one.

1. **04L (all galaxies)** on Kaggle with your `RAR_Universality_Research` dataset attached (it must contain `05_Results/Diagnostics/04_GP_Debugged/20261026T083032Z/` for the warm start). Download `04_GP_Debugged_<RUN_ID>.zip` from the Kaggle output and unzip it into `05_Results/Diagnostics/04_GP_Debugged/` on Drive. Note the RUN_ID.
2. **08X**: edit only its RUN SETTINGS cell. Put the 04L RUN_ID in `RAR_D_RUN_ID` every time.

   | Session | `RAR_SCENARIOS` | `RAR_KERNEL` | ≈ time |
   |---|---|---|---|
   | 1 | `A1` | `se` | 6 h |
   | 2 | `C1` | `se` | 6 h |
   | 3 | `C3` | `se` | 6 h |
   | 4 | `C4,C2` | `se` | 9 h |
   | 5 | `C4,C1` (`RAR_N_NULL` = `20`) | `matern32` | 5 h |
   | merge | `""` with `RAR_RESUME_FROM` = the four session folders, comma-separated | `se` | minutes |

   Sessions can run in parallel. The notebook never mixes kernels or Model D runs when merging, and seeds depend on the full plan, so sessions never share a mock.
3. **09 v4** on a GPU runtime: `RAR_RESUME_FROM` = `…/05_Results/Sensitivity/20261106T081353Z`, `RAR_RERUN_S3 = "1"`, `RAR_D_RUN_ID` = the 04L RUN_ID. S1 and S2 are reused; only S3 is refitted.
4. **Bring the results into this repository** (works for old and new runs alike, and is safe to repeat):

   ```bash
   python tools/collect_results.py "/path/to/Google Drive/My Drive/RAR_Universality_Research"
   python tools/headline_numbers.py          # prints the headline numbers from the newest runs, marks what changed
   git add results && git commit -m "Add results of runs <RUN_IDs>"
   ```

   If you do not use Google Drive for desktop, download the `05_Results` folder from drive.google.com, unzip it, and pass that path. `collect_results.py` copies reports, tables, configs, logs and figures, lists posterior files and archives (kept on Drive) in `results/LARGE_FILES.md`, and rebuilds the run table `results/RUNS.md`.

5. `headline_numbers.py` marks every headline value (family-wise rates, slopes beyond the cutoff, power, S3 slopes, Model D convergence) that differs from the earlier runs. When you adopt new runs as the reference, update `REFERENCE_RUNS` at the top of `tools/collect_results.py`.

## Data

SPARC (Lelli, McGaugh & Schombert 2016, AJ 152, 157) is public at <http://astroweb.cwru.edu/SPARC/>. It is not redistributed here; place the SPARC tables in the project's data folder as described at the top of Notebook 01, which audits them. Processed data, posterior samples (`.nc`) and checkpoints stay on Google Drive.

## Environment

Python ≥ 3.10 with the packages in `requirements.txt`. All notebooks run on free Colab or Kaggle CPUs; the dense-covariance S3 fit needs a GPU in practice (≈ 14× faster than CPU). Every run records its package versions in `config/`.

## Reproducibility notes

* Fixed seeds per notebook (recorded in each run's `config/*.json`).
* Decision rules and interpretation rules were written into each notebook before it was run.
* The full Model D fit used for the mocks (`20261026T083032Z`) is not fully converged ($\tau$ $\hat R$ = 1.029); results that depend on it are labelled provisional until the 04L run replaces it.

## Citation and licence

See `CITATION.cff`. Code is released under the MIT licence (`LICENSE`).

AI assistance: an AI assistant (Claude, Anthropic) helped write and debug the notebooks, and write documentation; the authors ran all analyses and are responsible for the content.
