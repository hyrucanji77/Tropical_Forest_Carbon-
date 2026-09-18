#!/usr/bin/env python3
"""Update the self-contained figures page from the current Figure 3 SVG.
Uses BeautifulSoup only for optional artwork authoring, not numerical reproduction.
"""
from pathlib import Path
from bs4 import BeautifulSoup
R=Path(__file__).resolve().parents[1]
p=R/'forest_carbon_figures.html'
soup=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
new=BeautifulSoup((R/'source_figures/figure_3_stand_structure.svg').read_text(),'html.parser').svg
new['id']='figure-3-svg';new['width']='100%';new['height']='auto';new['preserveAspectRatio']='xMidYMid meet'
new['aria-labelledby']='physical-title';new['aria-describedby']='physical-desc'
stage=soup.find(id='stage-3');stage.clear();stage.append(new)
heading=soup.find(id='figure-3-heading');heading.string='Independent measurements test the mapped target in both directions'
fig=soup.find(id='figure-3')
cap=fig.find('figcaption')
cap.clear()
cap.append(BeautifulSoup('''<strong>A two-sided test of the class-5 target.</strong>
Five explanations are evaluated: independent geometry, material properties, disjoint remainder compartments, spatial population selection, and <strong>overestimation in the mapped target</strong>. Held-out, geographically blocked plots and predictor-support diagnostics test the fifth explanation, including Baccini/Simard feature discrimination and extrapolation. A measured-minus-mapped residual can have either sign.
The published interval begins at <strong>478 MgC/ha</strong>; with illustrative carbon fraction 0.47, basic density 0.60 Mg/m³ and zero separate remainder, that model-class edge requires approximately <strong>1,020 Mg dry biomass/ha and 1,700 m³/ha</strong>. It is not an observed lower bound on every field plot or subpixel patch. The printed mean of 531.05 and stock/area ratio of 536.33 remain separate targets, both shown with rounded material requirements.<sup class="citations"><a href="#ref-4">4</a></sup>
The comparison table uses one fixed African or Amazonian biomass denominator per row, with separate columns for the two class-5 conventions.<sup class="citations"><a href="#ref-15">15</a><a href="#ref-16">16</a></sup>
Higuchi et al.’s dry-leaf sample-total fraction is <strong>1.05%</strong>, distinct from its mean fresh-mass percentage. A separate cloud-forest study estimates <strong>6.2 Mg/ha of living epiphytes</strong>, about 2% of reference biomass, while identifying dead organic matter separately. These population-specific observations do not support an arbitrary 65% nonwoody carbon remainder; woody liana stems remain woody components. The 10% carbon-remainder screen is a stated scenario, not a universal ecological ceiling.<sup class="citations"><a href="#ref-17">17</a><a href="#ref-18">18</a></sup>
The Córdoba aggregate audit reproduces measured basal-area summaries and source-method carbon, but its independent mapped residual is unidentified because sound volumes and map correspondence are absent. Class 5’s 5.31 million km² is comparable only in scale to a published historical Amazonian forest extent.<sup class="citations"><a href="#ref-11">11</a><a href="#ref-19">19</a></sup>''','html.parser'))
# Add network sources only if absent. Other references and their identifiers persist.
refs=soup.find(id='ref-14').parent
entries=[('15','Lewis, S. L., Sonké, B., Sunderland, T., et al. (2013).','Above-ground biomass and structure of 260 African tropical forests.','Philosophical Transactions of the Royal Society B, 368, 20120295. Source of the 395.7 Mg/ha network mean; 260 intact African plots.','10.1098/rstb.2012.0295'),('16','Malhi, Y., Wood, D., Baker, T. R., et al. (2006).','The regional variation of aboveground live biomass in old-growth Amazonian forests.','Global Change Biology, 12, 1107–1138. Source of the 200–350 Mg/ha regional comparison values.','10.1111/j.1365-2486.2006.01120.x')]
entries += [
 ('17','Higuchi, N., dos Santos, J., Ribeiro, R. J., Minette, L., & Biot, Y. (1998).','Biomassa da parte aérea da vegetação da floresta tropical úmida de terra-firme da Amazônia brasileira.','Acta Amazonica, 28(2), 153–166. Table 3(b): dry leaf and total mass means in a 38-tree nutrient subset.','10.1590/1809-43921998282166'),
 ('18','Gómez González, D. C., Rodríguez Quiel, C., Zotz, G., & Bader, M. Y. (2017).','Species richness and biomass of epiphytic vegetation in a tropical montane forest in western Panama.','Tropical Conservation Science, 10. Sampled masses and stand extrapolation; living and dead epiphytic material distinguished.','10.1177/1940082917698468'),
 ('19','Fauset, S., et al. (2015).','Hyperdominance in Amazonian forest carbon cycling.','Nature Communications, 6, 6857. Historical 5.3-million-km² extent used only for a scale comparison.','10.1038/ncomms7857')]
for num,authors,title,detail,doi in entries:
 if soup.find(id='ref-'+num):continue
 frag=BeautifulSoup(f'<li id="ref-{num}" tabindex="-1"><span aria-hidden="true" class="ref-number">{num}</span><div><p><span class="ref-authors">{authors}</span> <cite>{title}</cite> {detail}</p><div class="ref-links"><a href="https://doi.org/{doi}" target="_blank" rel="noopener noreferrer">doi:{doi}</a></div></div></li>','html.parser')
 refs.append(frag.li)
# Compact historical example; retains numerical status and source references.
hist=soup.find(id='historical-heading').parent
hist.clear()
hist.append(BeautifulSoup('''<h3 id="historical-heading">Historical 2010 illustration — not a 2025 emissions estimate</h3><div class="historical-grid"><div class="scenario"><strong class="value">26.16–32.61%</strong><span class="condition">Total held fixed</span></div><div class="scenario"><strong class="value">22.58–26.66%</strong><span class="condition">Other contributions retained</span></div><p>Both calculations impose the stock multiplier on Ecofys’s combined land-use category. Appendix B of the companion paper gives the complete assumptions and provenance.<sup class="citations"><a href="#ref-3">3</a><a href="#ref-9">9</a></sup></p></div><p class="historic-context">The published 26.15–32.60% endpoints are reproduced by truncation; a slightly different hidden baseline precision is also compatible. This is accounting arithmetic, not a measured annual forest contribution.</p>''','html.parser'))
ref9=soup.find(id='ref-9')
for text in list(ref9.find_all(string=True)):
 v=str(text).replace('6.3','6.5').replace('6.4','6.5').replace('Stand-structure closure, stock-to-flux identities and source-account comparability','A measurement protocol linking stand structure, carbon calibration and annual accounts')
 if v!=str(text):text.replace_with(v)
for text in list(soup.find_all(string=True)):
 if text.parent.name in ('script','style'):continue
 v=str(text).replace('companion 6.3','companion 6.5').replace('companion 6.4','companion 6.5').replace('V6.3','V6.5').replace('V6.4','V6.5').replace('v6_3','v6_5').replace('v6_4','v6_5')
 if v!=str(text):text.replace_with(v)
# Update any language that could retain a theorem claim for the stand definition.
for text in list(soup.find_all(string=True)):
 if text.parent.name in ('script','style'):continue
 v=str(text).replace('Stand-structure closure','Stand-carbon measurement protocol')
 if v!=str(text):text.replace_with(v)
p.write_text(str(soup),encoding='utf-8')
print('Updated the three-figure self-contained HTML, references and captions.')

# Frozen source citation and consistent physical-consequence panel.
soup=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
for node in soup.find_all(string=True):
 if node.parent.name in ('script','style'):continue
 v=str(node).replace('Difference from reference (%)','Shortfall from reference (%)')
 v=v.replace('A positive omitted net release increases atmospheric accumulation relative to a trajectory that omits it, unless other changes offset it.', "A positive net source missing from an account leaves actual accumulation above the account's reconstruction unless other terms offset it.")
 if v!=str(node):node.replace_with(v)
ref=soup.find(id='ref-9')
if ref:
 for a in ref.find_all('a',href=True):
  if 'github.com/hyrucanji77/Tropical_Forest_Carbon-' in a['href']:
   a['href']='https://github.com/hyrucanji77/Tropical_Forest_Carbon-/releases/tag/v6.5'
p.write_text(str(soup),encoding='utf-8')
