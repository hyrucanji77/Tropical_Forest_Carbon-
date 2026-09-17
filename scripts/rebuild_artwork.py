#!/usr/bin/env python3
"""Optional SVG -> vector PDF build (CairoSVG and a serif system font required).
Normal Overleaf use needs only the prebuilt PDFs. Geometry and palette are kept.
No font files are distributed. Run pdflatex figure_plates.tex after this script.
"""
from pathlib import Path

def main() -> None:
    try:
        import cairosvg
    except ImportError as exc:
        raise SystemExit('Install CairoSVG or use the included vector PDFs.') from exc
    root=Path(__file__).resolve().parents[1]
    for i,name in enumerate(('figure_1_reported_2025.svg','figure_2_forest_carbon_reassessment.svg'),1):
        svg=(root/'source_figures'/name).read_text(encoding='utf-8')
        svg=svg.replace('font-family:Source Serif 4,Georgia,Liberation Serif,serif','font-family:Liberation Serif')
        cairosvg.svg2pdf(bytestring=svg.encode(),write_to=str(root/'figures'/f'figure{i}.pdf'),
                        output_width=1716,output_height=1200,background_color='#f3f2f2')
        print(f'Built figures/figure{i}.pdf')
if __name__=='__main__': main()
