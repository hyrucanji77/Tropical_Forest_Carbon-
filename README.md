# Allometric calibration bias in tropical forest carbon

**Henry Arellano-Peña — NEBIOT S.A.S.**  
Architecture-informed measurement, LiDAR dependence and annual greenhouse-gas attribution.  
Publication edition **7.0**.

## Read

- `Allometric_Calibration_Bias_Manuscript.pdf`: main article.
- `Allometric_Calibration_Bias_Supplement.pdf`: technical derivations, conditional material comparisons and published-data provenance.
- `Allometric_Calibration_Bias_Figures.pdf`: three vector figure plates.

Architecture and organ allocation are mechanisms of allometric calibration bias. Increased LiDAR coverage cannot by itself remove a nonzero bias inherited from reference labels; direct 3D material reconstruction provides a distinct calibration pathway. The published 723.97 PgC result retains its mapped pantropical coverage, Australian-tropics exclusion and nominal 2007–2008 epoch. Annual emissions require disturbance, decomposition and removal information. The article does not report a new field inventory or a measured 2025 forest-loss percentage.

## Computational reproduction

```sh
python scripts/verify_public.py
```

Python 3.9 or later; standard library only. The verifier checks SHA-256 integrity, runs the numerical analysis in a temporary directory and compares **42 JSON/CSV outputs**. Temporary LaTeX table fragments are not published. The full author package reproduces 54 numerical/table outputs. The core suite has 257,167 assertions; later material/population suites add 6,623; a physical-volume regression adds one; the calibration-label suite adds 8,014. These checks test the specified algebra and transcriptions, not an independent forest inventory.

## Publication files and provenance

This distribution intentionally excludes `.tex`, HTML, SVG, document-build code and compressed source archives. Complete editable materials are delivered separately to the author. `PUBLICATION_MANIFEST.json` identifies the permitted file snapshot. `NUMERICAL_OUTPUTS.json` lists the regenerated public outputs. `SOURCE_AVAILABILITY.md` separates published source values from unrecovered original records.

The methodological focus and interpretations supersede the prior publication layout. The published source studies retain their original bibliographic attribution. Third-party data and methodology rights are described in `RIGHTS.md`. No Zenodo DOI is claimed. Publication in this repository is not a journal submission or replacement of the original arXiv preprint.
