# Allometric calibration bias in tropical forest carbon

**Henry Arellano-Peña — NEBIOT S.A.S.**  
Architecture-informed measurement, LiDAR dependence and annual greenhouse-gas attribution.  
Publication edition **7.5**, 18 September 2026 — corrected Figure 2 and compile-ready document edition.

## Read the current edition

- [Main article](Allometric_Calibration_Bias_Manuscript.pdf) — 30 pages, including the three figure plates.
- [Technical supplement](Allometric_Calibration_Bias_Supplement.pdf) — 18 pages.
- [Three vector figure plates](Allometric_Calibration_Bias_Figures.pdf).
- [Versioned release](https://github.com/hyrucanji77/Tropical_Forest_Carbon-/releases/tag/v7.5).

Architecture and organ allocation are mechanisms of allometric calibration bias. Greater LiDAR coverage cannot by itself remove a bias inherited from reference labels; independently checked three-dimensional material reconstruction offers a distinct calibration pathway. The initial 723.97 PgC estimate reported on arXiv retains its mapped pantropical coverage, Australian-tropics exclusion and nominal 2007–2008 epoch. Its annual implications require disturbance, decomposition and removal observations.

Figure 2 retains the questioned total, double-headed arrow and historical numerical interpretation. Its conditional largest-land-group example uses the specified 2010 Ecofys grouping; it is not a measured 2025 LULUCF ranking. The historical component heading is on two lines and its box is centered alongside the land-use sector. Standing stock remains separate from annual flows.

## Numerical reproduction

```sh
python scripts/verify_public.py
```

Python 3.9 or later; standard library only. The verifier checks the permitted publication files, verifies SHA-256 hashes, runs the analysis in a temporary directory, and checks **60 JSON/CSV outputs** for byte-identical regeneration. The complete author package regenerates 76 numerical/table outputs; temporary LaTeX table fragments are not published here. All recorded suite seeds, assertion counts and inference limits appear in `PUBLICATION_VERIFICATION.json`. These are analytical and transcription checks, not an independent field inventory.

## Distribution and provenance

The publication tree excludes LaTeX, HTML, SVG, document-build code and compressed archives. The editable Overleaf and webpage versions are supplied separately to the author. `PUBLICATION_MANIFEST.json` identifies the exact publication bytes; `NUMERICAL_OUTPUTS.json` lists generated public outputs. Original-record limitations and source conventions are documented in `SOURCE_AVAILABILITY.md` and the numerical provenance files.

Edition 7.5 supersedes the prior public edition. Obsolete active files and superseded release assets are retired after the replacement is verified; Git commit history is retained. The compiled scientific documents are copied unchanged from the approved compile-ready package. Historical source publications keep their original attribution. See `RIGHTS.md` for methodology and third-party rights. No archival DOI has been assigned, and repository publication is not a journal submission or arXiv replacement.
