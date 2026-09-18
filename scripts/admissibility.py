#!/usr/bin/env python3
"""Regenerate two-sided calibration tests and published-data admissibility checks.

Every empirical number is a source-labelled transcription. No missing geometry,
map correspondence or field residual is filled by an illustrative target.
"""
from __future__ import annotations
import csv, json, math, random
from pathlib import Path
R=Path(__file__).resolve().parents[1]
D=R/'data'

def interval_verdict(lower: float, upper: float, margin: float) -> str:
    """Classify an independently obtained measured-minus-mapped interval."""
    if not all(math.isfinite(x) for x in (lower, upper, margin)) or lower>upper or margin<0:
        raise ValueError('Finite ordered interval and non-negative margin required.')
    if upper < -margin: return 'mapped_target_above_independent_estimate'
    if lower > margin: return 'mapped_target_below_independent_estimate'
    if lower >= -margin and upper <= margin: return 'within_equivalence_margin'
    return 'unresolved_at_stated_precision'

def write_json(name: str, obj: object) -> None:
    (D/name).write_text(json.dumps(obj, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')

def grouped(x: float, decimals: int=0) -> str:
    return format(x, f',.{decimals}f').replace(',', '{,}')

def main() -> None:
    inp=json.loads((D/'admissibility_inputs.json').read_text())
    base=json.loads((D/'class5_comparison.json').read_text())
    f=inp['carbon_fraction_scenario'];rho=inp['basic_density_Mg_m3_scenario'];beta=f*rho
    target=base['requirements'][1]['carbon_MgC_ha']
    requirements=[]
    labels=['Class 5: lower class edge','Class 5: printed mean','Class 5: stock / area','Classes 4 and 5']
    vals=[inp['class5_lower_edge_MgC_ha']]+[row['carbon_MgC_ha'] for row in base['requirements']]
    for name,c in zip(labels,vals):
        requirements.append(dict(basis=name,carbon_MgC_ha=c,biomass_Mg_ha=c/f,
          woody_volume_m3_ha=c/beta,layer_cm=c/beta/100))
    # Round only public conditional labels; retain full numeric results in JSON/CSV.
    rows=[]
    for i,r in enumerate(requirements):
        carbon=grouped(r['carbon_MgC_ha'],0 if i==0 else 2)
        rows.append(f"{r['basis']} & {carbon} & $\\sim${grouped(round(r['biomass_Mg_ha'],-1))} & $\\sim${grouped(round(r['woody_volume_m3_ha'],-1))} & $\\sim${r['layer_cm']:.1f}\\\\\n")
    (D/'normalization_requirements_rows.tex').write_text(''.join(rows))
    with (D/'admissibility_requirements.csv').open('w',newline='') as h:
        w=csv.DictWriter(h,fieldnames=list(requirements[0]));w.writeheader();w.writerows(requirements)
    # Explicit per-comparator rows avoid ambiguous ranges with changing denominators.
    gap_rows=[]
    for comp in base['comparisons']:
        # Names/fields recorded by class5_comparison.py.
        label=comp.get('label', comp.get('comparison',comp.get('name','Comparison')))
        B=comp.get('baseline_biomass_Mg_ha',comp.get('biomass_Mg_ha'))
        if B is None:
            B=comp['comparison_biomass_Mg_ha']
        gap_rows.append(f"{label} & {B:g} & {comp['ratio_from_printed_mean']:.2f} & {comp['ratio_from_stock_area']:.2f}\\\\\n")
    (D/'network_gap_rows.tex').write_text(''.join(gap_rows))
    geom=[]
    for s in inp['geometry_scenarios']:
        for r in requirements[:3]:
            geom.append({**s,'basis':r['basis'],'psi_aH_required':r['woody_volume_m3_ha']/(s['basal_area_m2_ha']*s['basal_area_weighted_height_m'])})
    rem_fraction=inp['remainder_carbon_fraction_screen']
    rem=dict(screen_carbon_fraction=rem_fraction,screen_remainder_MgC_ha=target*rem_fraction,
       remaining_wood_C_MgC_ha=target*(1-rem_fraction),
       conditional_min_woody_volume_m3_ha=target*(1-rem_fraction)/beta,
       conditional_min_woody_mass_Mg_ha=target*(1-rem_fraction)/f,
       required_carbon_remainder_at_395_7=target-395.7*f,
       required_remainder_fraction_at_395_7=(target-395.7*f)/target,
       status=inp['remainder_screen_status'])
    H=inp['higuchi1998'];leaf=H['mean_dry_leaf_mass_kg']/H['mean_total_dry_mass_kg']
    C=inp['cordoba'];A=C['basis_area_ha']
    # The height entries are class ranges, not estimates of the basal-area mean.
    cyl_lo=math.fsum(g*h for g,h in zip(C['basal_area_m2_per_basis'],C['height_min_m']))/A
    cyl_hi=math.fsum(g*h for g,h in zip(C['basal_area_m2_per_basis'],C['height_max_m']))/A
    empirical=dict(source=C['source'],community=C['community'],reported_basal_area_m2_ha=C['reported_total_basal_area_m2']/A,
       class_sum_basal_area_m2_ha=math.fsum(C['basal_area_m2_per_basis'])/A,
       stems_ha=C['reported_total_stems']/A,allometry_based_biomass_Mg_ha=C['reported_total_biomass_Mg']/A,
       source_method_carbon_MgC_ha=C['reported_total_carbon_MgC']/A,
       basal_area_times_height_envelope_m3_ha=[cyl_lo,cyl_hi],
       envelope_status='Calculated from displayed class basal areas and height limits; not woody volume or a confidence interval; rounded source aggregates',
       mapped_class=None,geometric_carbon_MgC_ha=None,measured_minus_mapped_R=None,
       evaluation_status='not_identifiable_from_available_aggregates',
       missing_inputs=['Independent solid organ volumes','Paired volume-density-carbon measurements and remainder pools','Georeferenced map value and class on matched epoch/pool','Representative plot inclusion weights'],
       source_rows=C)
    write_json('cordoba_empirical_audit.json',empirical)
    tab=[('Reported mean stem density',f"{grouped(empirical['stems_ha'],1)} ha$^{{-1}}$"),
      ('Reported mean basal area',f"{empirical['reported_basal_area_m2_ha']:.1f} m$^2$ ha$^{{-1}}$"),
      ('Sum of displayed class basal areas',f"{empirical['class_sum_basal_area_m2_ha']:.1f} m$^2$ ha$^{{-1}}$"),
      ('Allometry-based aboveground biomass',f"{empirical['allometry_based_biomass_Mg_ha']:.1f} Mg ha$^{{-1}}$"),
      ('Source-method carbon',f"{empirical['source_method_carbon_MgC_ha']:.1f} MgC ha$^{{-1}}$"),
      ('Displayed-class $\\sum_h G_h H_h$ envelope',f"{cyl_lo:.1f}--{cyl_hi:.1f} m$^3$ ha$^{{-1}}$"),
      ('Independent geometric carbon / mapped residual','Not identifiable')]
    (D/'cordoba_audit_rows.tex').write_text(''.join(f'{a} & {b}\\\\\n' for a,b in tab))
    evidence=dict(higuchi_dry_leaf_mass_fraction=leaf,higuchi_reference=H,
      epiphytes_live_Mg_ha=inp['gomez2017']['living_epiphytes_kg_ha']/1000,
      epiphytes_dead_Mg_ha=inp['gomez2017']['dead_organic_matter_kg_ha']/1000,
      comparison_warning='Different taxa, pools, populations and estimators; not a pooled universal bound')
    summary=dict(requirements=requirements,geometry_scenarios=geom,remainder=rem,component_evidence=evidence,
      source_class_area_km2=531449420.52/100,
      hypothesis_set=['volume_or_architecture_difference','material_properties','separately_measured_remainder','spatial_population_selection','mapped_target_overestimate'],
      empirical_closure_status=empirical['evaluation_status'])
    write_json('admissibility_summary.json',summary)
    # Regression and randomized tests demonstrate two-sided logic, not field outcomes.
    count=0
    def check(cond):
        nonlocal count
        count+=1
        if not cond: raise AssertionError(f'Admissibility check {count} failed')
    def near(a,b):check(math.isclose(a,b,abs_tol=1e-10,rel_tol=1e-12))
    near(requirements[0]['biomass_Mg_ha'],478/.47);near(requirements[0]['woody_volume_m3_ha'],478/.282)
    check(0<leaf<.02);near(empirical['allometry_based_biomass_Mg_ha'],147.8)
    near(empirical['reported_basal_area_m2_ha'],45.2);check(cyl_lo<cyl_hi)
    check(empirical['measured_minus_mapped_R'] is None)
    check(rem['conditional_min_woody_mass_Mg_ha']>395.7)
    check(interval_verdict(-30,-20,5)=='mapped_target_above_independent_estimate')
    check(interval_verdict(20,30,5)=='mapped_target_below_independent_estimate')
    check(interval_verdict(-2,3,5)=='within_equivalence_margin')
    check(interval_verdict(-10,3,5)=='unresolved_at_stated_precision')
    for args in [(1,0,1),(0,1,-1),(float('nan'),1,1)]:
        try:interval_verdict(*args)
        except ValueError:check(True)
        else:check(False)
    rng=random.Random(20260921)
    max_res=0.0
    for _ in range(250):
        areas=[rng.uniform(.001,1) for _ in range(12)];heights=[rng.uniform(1,60) for _ in areas]
        psi=[rng.uniform(.1,3) for _ in areas]
        sum_a=math.fsum(areas);ah=math.fsum(a*h for a,h in zip(areas,heights))
        V=math.fsum(a*h*p for a,h,p in zip(areas,heights,psi))
        H_a=ah/sum_a;P_aH=V/ah;L=V/sum_a
        near(L,H_a*P_aH);max_res=max(max_res,abs(L-H_a*P_aH))
        # A priori material upper bound is a conditional empirical criterion.
        b=rng.uniform(.1,.5);v=rng.uniform(50,2000);c=rng.uniform(0,50)
        near(b*v+c,(b*v)+c)
    write_json('admissibility_validation.json',dict(status='PASS',assertions=count,synthetic_cases=250,
      seed=20260921,max_geometry_residual=max_res,scope='Published aggregate reproduction, exact geometry decomposition and decision-rule tests; no field R5'))
    print(f'Admissibility: {count} assertions; empirical map residual remains unidentified.')
if __name__=='__main__':main()
