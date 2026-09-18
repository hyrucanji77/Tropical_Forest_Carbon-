#!/usr/bin/env python3
"""Reproduce the two class-5 conventions and explicit comparison sensitivities.

No field data are generated. Source-reported network estimates have different
populations and are not treated as matched class-5 measurements. Python >=3.9,
standard library, deterministic; run without -O.
"""
from __future__ import annotations
import csv, json, math
from pathlib import Path
R=Path(__file__).resolve().parents[1]
D=R/'data'

def dump(name, obj):
    (D/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def csvfile(name, rows):
    with (D/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def required_volume(carbon: float, beta: float, remainder: float=0) -> float:
    if any(not math.isfinite(v) for v in (carbon,beta,remainder)):
        raise ValueError('Finite values required')
    if beta<=0 or carbon<0 or remainder<0 or remainder>carbon:
        raise ValueError('Positive beta and 0 <= remainder <= carbon required')
    return (carbon-remainder)/beta

def main():
    if not __debug__:raise RuntimeError('Run without -O.')
    cfg=json.loads((D/'class5_comparison_inputs.json').read_text())
    old=json.loads((D/'inputs.json').read_text())['density_audit']
    r5=next(x for x in old['rows'] if x['class']==5)
    pair=[x for x in old['rows'] if x['class'] in (4,5)]
    c=r5['stock_pgc']*1e9/r5['area_ha']; p=r5['printed_density']
    pair_c=math.fsum(x['stock_pgc'] for x in pair)*1e9/math.fsum(x['area_ha'] for x in pair)
    f=cfg['illustrative_carbon_fraction'];rho=cfg['illustrative_basic_density_Mg_m3'];beta=f*rho
    bases=[('Class 5: printed mean',p),('Class 5: stock / area',c),('Classes 4 and 5',pair_c)]
    rows=[]
    for label,cc in bases:
        v=required_volume(cc,beta)
        rows.append(dict(basis=label,carbon_MgC_ha=cc,conditional_biomass_Mg_ha=cc/f,
                    woody_volume_m3_ha=v,equivalent_layer_cm=v/100,
                    carbon_fraction=f,basic_density_Mg_m3=rho,remainder_MgC_ha=0))
    comparisons=[]
    for comp in cfg['comparisons']:
        b=comp['biomass_Mg_ha']
        comparisons.append(dict(source_key=comp['key'],label=comp['label'],comparison_biomass_Mg_ha=b,
                     ratio_target_biomass_Mg_ha=c/f,printed_target_biomass_Mg_ha=p/f,
                     ratio_from_stock_area=(c/f)/b,ratio_from_printed_mean=(p/f)/b,
                     excess_from_stock_area_Mg_ha=c/f-b,doi=comp['doi']))
    sens=[dict(beta_MgC_m3=b,carbon_target_MgC_ha=c,remainder_MgC_ha=0,
               required_volume_m3_ha=required_volume(c,b),dvolume_dbeta=-c/b**2)
           for b in cfg['beta_sensitivities_MgC_m3']]
    hypothetical_B=cfg['comparisons'][0]['biomass_Mg_ha']
    remainder=c-hypothetical_B*f
    detail={'requirements':rows,'comparisons':comparisons,'beta_sensitivity':sens,
       'normalization_biomass_change_percent':100*(1-p/c),
       'hypothetical_remainder':{'hypothetical_matched_woody_mass_Mg_ha':hypothetical_B,
           'assumed_carbon_fraction':f,'woody_carbon_MgC_ha':hypothetical_B*f,
           'required_other_aboveground_carbon_MgC_ha':remainder,
           'target_share_percent':100*remainder/c,
           'status':'Scale calculation, not a finding that Lewis et al. omitted this amount; actual source pool coverage must be matched.'},
       'evidence_status':'Calculated comparisons and sensitivities only; no recovered or simulated field observations.'}
    dump('class5_comparison.json',detail)
    csvfile('class5_comparisons.csv',comparisons)
    csvfile('material_sensitivity.csv',sens)
    out=[]
    for r in rows:
        out.append(f"{r['basis']} & {r['carbon_MgC_ha']:.2f} & {r['conditional_biomass_Mg_ha']:.2f} & {r['woody_volume_m3_ha']:.2f} & {r['equivalent_layer_cm']:.2f} "+r'\\')
    (D/'normalization_requirements_rows.tex').write_text('\n'.join(out)+'\n')
    out=[]
    for r in comparisons:
        out.append(r['label']+r' \citep{'+r['source_key']+'}'+f" & {r['comparison_biomass_Mg_ha']:.1f} & {r['ratio_from_stock_area']:.2f} & {r['excess_from_stock_area_Mg_ha']:.2f} "+r'\\')
    (D/'network_gap_rows.tex').write_text('\n'.join(out)+'\n')
    checks=0;maxres=0
    def check(condition):
        nonlocal checks
        checks+=1
        if not condition:raise AssertionError('class-5 comparison check '+str(checks))
    def close(a,b):
        nonlocal maxres
        maxres=max(maxres,abs(a-b));check(math.isclose(a,b,abs_tol=1e-10,rel_tol=1e-12))
    for r in rows:
        close(r['conditional_biomass_Mg_ha']*f,r['carbon_MgC_ha'])
        close(r['woody_volume_m3_ha']*rho,r['conditional_biomass_Mg_ha'])
        close(r['equivalent_layer_cm']*100,r['woody_volume_m3_ha'])
    check(round(c,4)==536.3257);check(round(p/f,2)==1129.89)
    check(round(c/f,2)==1141.12);check(round(required_volume(p,beta),2)==1883.16)
    for r in comparisons:
        close(r['ratio_from_stock_area']*r['comparison_biomass_Mg_ha'],c/f)
        close(r['ratio_from_printed_mean']*r['comparison_biomass_Mg_ha'],p/f)
        close(r['excess_from_stock_area_Mg_ha']+r['comparison_biomass_Mg_ha'],c/f)
    check(round(comparisons[0]['ratio_from_stock_area'],2)==2.88)
    check(round(comparisons[0]['ratio_from_printed_mean'],2)==2.86)
    check(required_volume(c,.25)>required_volume(c,.282)>required_volume(c,.30))
    for b in (.25,.282,.30):
        close(required_volume(c,b,remainder),hypothetical_B*f/b)
        close(required_volume(c,b)-required_volume(c,b,20),20/b)
        check(required_volume(c,b)>=0)
    close(hypothetical_B*f+remainder,c);check(round(100*remainder/c,1)==65.3)
    # Same volume can represent different amounts only via measured material changes;
    # a completely matched dry total bounds the carbon contained in that total.
    for fraction in (.4111,.47,.4999,1):check(hypothetical_B*fraction<=hypothetical_B)
    # Direct membership reproduces the table correction without a combinatorial argument.
    intervals={r['class']:r['range_mgc_ha'] for r in old['rows']}
    assignment=[]
    for r in old['rows']:
        ratio=r['stock_pgc']*1e9/r['area_ha']
        matches=[k for k,(lo,hi) in intervals.items() if lo<ratio<hi and lo<r['printed_density']<hi]
        check(len(matches)==1);assignment.append(matches[0])
    check(assignment==[5,4,3,2,1])
    # A common class-level area factor does not force pointwise constant distortion.
    q=.99016;m=1/q
    areas_A=[m-.02,m+.02];areas_B=[m-.035,m+.035]
    close(1/(sum(areas_A)/2),q);close(1/(sum(areas_B)/2),q)
    check(areas_A!=areas_B);check(areas_A[0]!=areas_A[1])
    for args in [(c,0,0),(c,-1,0),(c,.282,-1),(c,.282,c+1),(c,float('nan'),0)]:
        try:required_volume(*args)
        except ValueError:check(True)
        else:check(False)
    dump('class5_comparison_validation.json',{'status':'PASS','deterministic_assertions':checks,
      'max_arithmetic_residual':maxres,'direct_interval_assignment':assignment,
      'scope':'Published-input arithmetic, physical sensitivity signs and logical counterexamples; not field validation.'})
    print(f'Class-5 comparison: {checks} deterministic assertions passed.')

if __name__=='__main__':main()
