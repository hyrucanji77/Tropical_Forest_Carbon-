#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if command -v bibtex >/dev/null 2>&1 && bibtex --version >/dev/null 2>&1; then
  BIBTEX=bibtex
elif command -v bibtex.original >/dev/null 2>&1; then
  BIBTEX=bibtex.original
elif command -v bibtex8 >/dev/null 2>&1; then
  BIBTEX=bibtex8
else
  echo "BibTeX is required. The included PDFs remain readable without it." >&2
  exit 1
fi
for document in main response_to_review; do
  pdflatex -interaction=nonstopmode -halt-on-error "$document.tex"
  "$BIBTEX" "$document"
  pdflatex -interaction=nonstopmode -halt-on-error "$document.tex"
  pdflatex -interaction=nonstopmode -halt-on-error "$document.tex"
done
