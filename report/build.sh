#!/bin/sh
# Build report.pdf (repo root) from report/report.tex. Needs pdflatex; diagrams need Chromium:
#   python experiment/scripts/render_diagrams.py [chrome]   # report/fig/*.mmd -> report/fig/*.pdf
set -e
cd "$(dirname "$0")"
pdflatex -interaction=nonstopmode -halt-on-error report.tex >/dev/null
pdflatex -interaction=nonstopmode -halt-on-error report.tex >/dev/null
cp report.pdf ../report.pdf
rm -f report.aux report.log report.out report.pdf
echo "wrote report.pdf"
