# From tropical forest-carbon measurement to annual carbon accounts

**Henry Arellano-Peña — NEBIOT S.A.S.**  
A measurement protocol linking stand structure, carbon calibration and annual accounts.  
**Frozen release 6.5 · 17 September 2026**

## Read and download

[Versioned release](https://github.com/hyrucanji77/Tropical_Forest_Carbon-/releases/tag/v6.5) · [Manuscript](main.pdf) · [Overleaf archive](release/Tropical_Forest_Carbon_Overleaf_v6_5.zip) · [Figures webpage](forest_carbon_figures.html) · [Three vector plates](figures/figure_plates.pdf)

Upload the Overleaf ZIP as an existing project and compile `main.tex` with pdfLaTeX. Prebuilt vector figure PDFs, bibliography and numerical tables are included. Ordinary Overleaf compilation needs no Python execution, network retrieval, external fonts or shell escape. `response_to_review.pdf` contains separate methodological and source notes, not an internal discussion transcript.

The manuscript identifies the mapped pantropical estimate of 723.97 PgC, the exclusion of the Australian tropics, and the nominal 2007–2008 map epoch. Its independent protocol tests corroboration, downward revision and upward revision against representative measurements, while reporting uncertainty-overlapping comparisons as unresolved. The class-5 structural requirements remain explicit scenarios, not fabricated field observations.

## Reproduce and verify

```sh
python scripts/verify_package.py
python scripts/reproduce.py
bash scripts/build_local.sh
```

Python 3.9 or later and its standard library suffice for numerical work; run without `-O`. The verifier regenerates **51 numerical/table files**. JSON/CSV numerical comparisons permit absolute tolerance 1e-10 and relative tolerance 1e-12 across platforms; exact decimal strings, labels and LaTeX fragments are exact. The report also states whether regeneration is byte-identical. Verify before recompiling PDFs, since compilation can change metadata.

| Check programme | Cases and seed | Reported checks |
|---|---|---:|
| Core plus analytical/audit extensions | 1,000 / 20260916; 20,000 / 20260917; 1,100 / 20260918 | 257,167 |
| Population and atmosphere | Deterministic | 40 |
| Physical closure | 1,000 / 20260919 | 6,013 |
| Class-5 comparison | Deterministic | 55 |
| Admissibility and Córdoba inputs | 250 / 20260921 | 515 |
| **Total of these reported suites** | | **263,790** |

`measurement_evidence.py` performs one additional regression assertion on the four displayed physical-validation shortfalls. These checks reproduce mathematics and published inputs; they do not validate an unmeasured class-5 population or a new emissions inventory.

## Data and measurements

`data/inputs.json` preserves the source table. `data/source_provenance.csv` documents references, periods and inference limits. The measurement schema, observed-data eligibility check and `SOURCE_AVAILABILITY.md` identify absent independent geometry and map correspondence. No private client material or font files are distributed.

To evaluate independent measured records, use:

```sh
python scripts/physical_closure.py --measurements measured.json --output measured_closure.json
```

Do not populate the schema by back-calculating geometry from the mapped target. The evaluator checks input and material arithmetic; it cannot authenticate records or supply missing sampling weights.

## Complete build

```sh
python scripts/reproduce.py
python scripts/build_physical_figure.py
python scripts/rebuild_artwork.py
python scripts/build_companion_html.py
pdflatex -interaction=nonstopmode -halt-on-error figure_plates.tex
cp figure_plates.pdf figures/figure_plates.pdf
bash scripts/build_local.sh
python scripts/make_manifest.py
python scripts/verify_package.py > verification.json
python scripts/package_release.py
```

Artwork regeneration additionally requires CairoSVG and BeautifulSoup. `scripts/build_local.sh` uses pdfLaTeX and BibTeX. The release archive is extracted and verified before distribution. The manifest and `release/release.json` record SHA-256 checksums.

## Citation, rights and deposit

Use `CITATION.cff` or the release URL above to cite this frozen edition. **No archival DOI is assigned.** `zenodo_metadata.json` is metadata for a possible later authenticated deposit, not proof of one.

The author owns the methods examined and is founder/director of NEBIOT, the only current company affiliation. The manuscript states the NEB001/NEB002 relationship, funding statement and assistance disclosures. Published source citations retain their bibliographic identities. `RIGHTS.md` distinguishes methodological ownership, EDGAR data attribution and third-party diagram-design provenance.

The current repository tree and release list contain this edition only. Historical Git commits are preserved for provenance; removal of obsolete downloads does not rewrite Git history. No journal submission or replacement of the original preprint is represented by this repository release.
