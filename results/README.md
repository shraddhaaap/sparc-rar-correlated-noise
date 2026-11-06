# Results

`05_Results/` mirrors the `05_Results/` folder of the project on Google Drive. Each notebook run has its own timestamped folder (UTC), so runs never overwrite each other and new runs merge simply by adding folders.

* Fill or refresh it with `python tools/collect_results.py <path to RAR_Universality_Research>`; it is safe to repeat.
* `RUNS.md` lists every run, the notebook that made it, its integrity-check status, its report, and whether it is a reference run.
* `LARGE_FILES.md` lists posterior samples, checkpoints and archives that stay on Drive.

This snapshot already contains the fit-level results of the Notebook 08 v2 reference run (`Injection_Recovery_Extended/20261105T161628Z/tables/08_mock_fit_results.csv`). Run `collect_results.py` once on your Drive folder to add all remaining tables, reports and figures.
