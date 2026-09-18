#!/usr/bin/env python3
"""Build a precise vector plate for two-sided class-5 calibration tests."""
from pathlib import Path
from html import escape
import json
R=Path(__file__).resolve().parents[1]
D=json.loads((R/'data/admissibility_summary.json').read_text())
B=json.loads((R/'data/class5_comparison.json').read_text())
PAPER='#f3f2f2';INK='#201e1d';GREEN='#186D30';BLUE='#006786';LINE='#bab6b6';SOFT='#e8eee8'
p=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2288 1600" role="img" aria-labelledby="physical-title physical-desc" style="font-family:Source Serif 4,Georgia,Liberation Serif,serif">',
'<title id="physical-title">Independent stand measurements test the mapped target in both directions</title>',
'<desc id="physical-desc">Five explanations are tested: volume, material properties, remainder compartments, spatial selection and an overestimated mapped target. Class-5 lower edge is a model-class threshold, not a measured field lower bound. Conditional requirements are rounded. Independent measured-minus-mapped residuals can support or reject the target.</desc>',f'<rect width="2288" height="1600" fill="{PAPER}"/>']
def box(x,y,w,h,fill=PAPER,stroke=LINE,sw=1):p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
def txt(x,y,s,size=27,color=INK,bold=False,anchor='start'):p.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{600 if bold else 400}" text-anchor="{anchor}">{escape(s)}</text>')
def line(x,y,x2,color=LINE,w=1):p.append(f'<path d="M{x} {y}H{x2}" stroke="{color}" stroke-width="{w}"/>')
def lines(x,y,items,size=25,step=35,color=INK):
 for j,s in enumerate(items):txt(x,y+j*step,s,size,color)
txt(52,42,'INDEPENDENT MEASUREMENT → FORWARD RECONSTRUCTION → TWO-SIDED TEST',26,BLUE,True);line(52,62,2236,INK,2)
for x,title in [(52,'01  MEASURE'),(800,'02  RECONSTRUCT'),(1548,'03  COMPARE')]:
 box(x,88,688,206,SOFT if x==800 else PAPER);txt(x+24,128,title,26,BLUE,True)
lines(76,176,['Stems, basal area, heights and sound organ volume','Paired material density and carbon fraction','Independent plots; fixed epoch and class'],24,38)
lines(824,176,['Carbon / ha = β × G × Λ + remainder','Λ = weighted height × weighted architecture','Average plot products; retain covariance'],26,38,GREEN)
lines(1572,176,['Independent measured minus mapped carbon','R < 0 can support an overestimated map','R > 0 can support an underestimated map'],25,38)
txt(52,337,'CLASS 5 · 531.45 MILLION HECTARES · ABOUT 5.31 MILLION km²',27,BLUE,True)
txt(52,370,'Comparable in scale to the historical Amazonian forest extent; not the same domain or a current area estimate.',23)
box(52,396,1225,325);box(1330,396,906,325)
txt(76,435,'Density basis',24,INK,True)
for x,t in [(683,'MgC/ha'),(914,'Mg dry/ha'),(1250,'m³/ha')]:txt(x,435,t,24,INK,True,'end')
line(76,453,1252)
labels=['Class 5: lower class edge','Class 5: printed mean','Class 5: stock / area','Classes 4 and 5']
for j,(name,row) in enumerate(zip(labels,D['requirements'])):
 y=494+j*50
 txt(76,y,name,25,INK,True)
 txt(683,y,f"{row['carbon_MgC_ha']:.0f}" if j==0 else f"{row['carbon_MgC_ha']:.2f}",27,GREEN,True,'end')
 txt(914,y,'≈ '+f"{round(row['biomass_Mg_ha'],-1):,.0f}",27,GREEN,True,'end')
 txt(1250,y,'≈ '+f"{round(row['woody_volume_m3_ha'],-1):,.0f}",27,GREEN,True,'end')
txt(76,692,'Illustrative f = 0.47; ρ = 0.60 Mg/m³; separate remainder = 0.',22)
txt(1352,432,'Fixed biomass denominator',24,INK,True)
txt(2070,432,'Printed',23,INK,True,'end');txt(2215,432,'Ratio',23,INK,True,'end');line(1352,453,2215)
for j,(name,row) in enumerate(zip(['African mean: 395.7 Mg/ha','Amazonian value: 350 Mg/ha','Amazonian value: 200 Mg/ha'],B['comparisons'])):
 y=494+j*50;txt(1352,y,name,24)
 txt(2070,y,f"{row['ratio_from_printed_mean']:.2f}×",27,GREEN,True,'end')
 txt(2215,y,f"{row['ratio_from_stock_area']:.2f}×",27,GREEN,True,'end')
lines(1352,654,['Factors compare different populations and estimators.','Each column changes only the class-5 convention.'],22,32)
box(52,749,2184,103,SOFT,GREEN,1)
lines(76,785,['Model-class edge 478: applies to assigned cell estimates if the class rules are implemented; not every field plot or subpixel patch.',
 'At weighted height 30 m: G = 30 / 40 m²/ha requires weighted ψ ≈ 2.1 / 1.6 at the ratio target. These are scenarios, not observed stands.'],24,39)
txt(52,895,'FIVE EXPLANATIONS AND THE OBSERVATIONS THAT DISCRIMINATE THEM',26,BLUE,True)
rows=[
 ('1  Solid volume / architecture',['Measure sound stems, branches, taper and cavities independently.','A large ψ inferred from the carbon target does not test that target.']),
 ('2  Material properties',['Measure paired density and carbon fractions across organs and strata.','Lower β raises required wood volume; β is not an adjustable fit coefficient.']),
 ('3  Remainder compartments',['Foliage ≈ 1.05% of dry mass in a harvested-tree subset; live epiphytes ≈ 2% in one stand.','A 65% carbon remainder is unsupported by these examples. Woody lianas stay in woody accounting.']),
 ('4  Spatial population selection',['Match the class map to independent, representative field strata and sampling weights.','Different forest populations can differ physically; a selected exceptional hectare is insufficient.']),
 ('5  Mapped target overestimated',['Test map calibration, out-of-domain prediction and Baccini/Simard predictor discrimination.','Held-out plots and negative residuals beyond a prespecified margin discriminate upward map bias.'])]
for j,(name,ss) in enumerate(rows):
 y=918+j*90;box(52,y,2184,90,SOFT if j==4 else PAPER,GREEN if j==4 else LINE,2 if j==4 else 1)
 txt(76,y+39,name,27,GREEN,True);lines(688,y+33,ss,24,34)
line(52,1390,2236,INK,2)
lines(52,1433,['DECISION: compare a joint-uncertainty interval for R with a prespecified equivalence margin in both directions.',
 'Current empirical application: Córdoba aggregates are reproduced; independent volume and matched map values are missing, so R is unidentified.',
 'Foliage and epiphyte examples are population-specific. A 10% remainder screen is an explicit scenario, not a universal ecological ceiling.'],24,38)
txt(52,1574,'Sources: Arellano-P. & Rangel-Ch. (2016); Lewis (2013); Malhi (2006); Higuchi (1998); Gómez González (2017); Vásquez & Arellano (2012).',22)
p.append('</svg>');(R/'source_figures/figure_3_stand_structure.svg').write_text('\n'.join(p))
print('Built Figure 3: five explanations and a two-sided mapped-target test.')
