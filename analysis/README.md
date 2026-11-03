# Analysis files

| Folder | Content |
|---|---|
| `opensim_check/` | Independent OpenSim 4.6 cross-check of the graft path (model `gh_from_app.osim`, `os_model.py`, `os_crosscheck.py`, geometry and results). Run with OpenSim's Python bindings. |
| `insilico/` | Cadaver tendon dimensions (exact confidence interval, right-left Spearman and Wilcoxon) and variation of the graft path across four CT shoulders (`variab.json`, CSV tables). `analysis.py` needs the cadaver workbook, which is not included; its per-shoulder values are in `index.html` (`CAD.rows`). |
| `pilot_exploratory/` | Exploratory in silico study of the effect of graft stiffness and muscle loads. Not validated; see its README. |

The four CT shoulders come from the open dataset Henninger et al. (Zenodo 14590062, CC BY 4.0). No patient data are included.
