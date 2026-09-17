# From tropical forest-carbon measurement to annual carbon accounts

**Henry Arellano-Peña — NEBIOT S.A.S.**  
Stock-to-flux identities, census calibration and a historical-data audit.  
Research snapshot **5.0**, 16 September 2026.

Repository: https://github.com/hyrucanji77/Tropical_Forest_Carbon-

## Read or use Overleaf

`main.pdf` is the paper; `main.tex` is its complete editable LaTeX source. `figures/figure_plates.pdf` contains the two large-format vector plates. `response_to_review.pdf` and its LaTeX source are separate from the paper. The complete Overleaf ZIP is in `release/` after the build finishes.

For Overleaf, upload the ZIP as an existing project and compile `main.tex` with pdfLaTeX. Figure PDFs, bibliography and generated numerical tables are included, so normal document compilation requires no Python execution, external fonts, network retrieval or shell escape. Locally, run `bash scripts/build_local.sh`.

## Reproduce the research

```sh
python scripts/verify_package.py
python scripts/reproduce.py
```

Python 3.9 or later, standard library only, without `-O`. Verification checks SHA-256 integrity, regenerates 26 numerical/table files, compares results and restores the manifest-backed snapshot. Numerical JSON/CSV values allow absolute tolerance 1e-10 and relative tolerance 1e-12 across platforms; exact decimal strings, labels and LaTeX fragments remain exact. The result states whether all files also reproduce byte-for-byte. Compiling PDFs can change their metadata, so verify integrity before rebuilding.

The test programme has 22,100 seeded randomized cases plus regression and invalid-input checks. Exact assertion counts and residuals are in `data/validation.json`. These checks test specified calculations and analytical identities; they do not validate a forest-carbon stock or estimate a new annual emissions inventory.

## Main results

The weighted-mean covariance identity specifies which association transfers carbon-stock correction into release. The paired-account identities distinguish emissions, removals, zero-stock regrowth and mortality/growth calibration. Exact quadratic and finite-interval power-law criteria supply calibration-specific census screens. The annual-cohort convolution distinguishes a clearing cohort's first-year timing from a mixed annual inventory.

The published-digit audit transcribes the historical preprint table, tests nearest rounding and truncation separately, and diagnoses a shared normalization and crossed class intervals. Subset comparisons distinguish a conditional lower bound from an assumed whole-domain-density benchmark. Historical percentage calculations retain their original accounting and unresolved provenance rather than becoming 2025 measurements.

## Data and provenance

- `data/inputs.json`: displayed historical inputs, contemporary reference values and labelled synthetic scenarios.
- `data/source_provenance.csv`: source URLs, versions, locations and inference limits.
- `data/display_precision_audit.json`: exact decimal interval and rational-probability diagnostics.
- `data/annual_cohort_examples.csv`: constant, increasing and decreasing clearing examples.
- `scripts/`: executable numerical analysis, verification, artwork and packaging tools.
- `source_figures/`: editable SVGs; `figures/`: compiled vector artwork.
- `manifest.json`, `verification.json`, `release/release.json`: snapshot integrity, computation and package records.

See `SOURCE_AVAILABILITY.md` for the empirical records that were not recovered. No private client files, original third-party datasets or font files are distributed. This deposit has a repository URL and commit history; **no Zenodo DOI is claimed**.

## Rebuild the complete snapshot

```sh
python scripts/reproduce.py
python scripts/rebuild_artwork.py  # optional; requires CairoSVG and a serif system font
pdflatex figure_plates.tex
# Copy figure_plates.pdf into figures/figure_plates.pdf.
bash scripts/build_local.sh
python scripts/make_manifest.py
python scripts/verify_package.py > verification.json
python scripts/package_release.py
```

The GitHub build workflow performs these steps. A build-generated commit records the source revision used. Read the immutable commit URL when citing a particular snapshot rather than assuming `main` never changes.

## Attribution and declarations

The author is the sole author of this paper, owns the methodologies discussed and is founder/director of NEBIOT, the only company currently affiliated with the work. The paper records the author's no-competing-interests declaration and the specific NEB001/NEB002 methodological connection. It states that no external funding is reported and discloses ChatGPT and Claude assistance. Earlier publications retain their published author lists in citations.

The diagram organization credits WRI and Ecofys; EDGAR's data are identified separately. `RIGHTS.md` distinguishes the report's licence from third-party artwork and proprietary methodology rights. The repository does not grant a blanket licence to protected third-party material or to the underlying NEB methodologies.
