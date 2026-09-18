#!/usr/bin/env python3
"""Forward stand-geometry closure and published-table diagnostics.

Python >=3.9, standard library. Running this module regenerates ONLY derived
requirements and synthetic algebra checks. It does not manufacture class-5
observations. To evaluate measured records, use --measurements path.json
--output result.json; records must conform to data/stand_measurement_schema.json.
All observed quantities must come from independent measurements, not a fit to
the carbon target. The algebraic closure itself is an internal identity.
"""
from __future__ import annotations
import argparse
import csv
import itertools
import json
import math
import random
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'


def number(x: Any, name: str, positive: bool = False) -> float:
    if isinstance(x, bool):
        raise ValueError(name + ': boolean is not a measurement')
    v = float(x)
    if not math.isfinite(v) or (v <= 0 if positive else v < 0):
        raise ValueError(name + ': invalid finite nonnegative/positive value')
    return v


def plot_closure(record: dict[str, Any]) -> dict[str, Any]:
    """Reconstruct carbon from disjoint material volumes for one sampled plot.

    Only compartments explicitly flagged `woody` enter G*Lambda. Other carbon
    enters the remainder. Basal area is an independently supplied cross-section,
    not inferred from biomass. Plots/trees/compartments must use a matched epoch
    and ownership convention for crown material crossing the plot boundary.
    """
    A = number(record['plot_area_ha'], 'plot_area_ha', True)
    trees = record['trees']
    if not isinstance(trees, list) or not trees:
        raise ValueError('At least one measured tree record is required')
    tree_ids: set[str] = set()
    area, volumes, heights, wood_c, rest_c, profiles = [], [], [], [], [], []
    for tree in trees:
        ident = str(tree['tree_id'])
        if not ident or ident in tree_ids:
            raise ValueError('Tree identifiers must be nonempty and unique')
        tree_ids.add(ident)
        a = number(tree['basal_area_m2'], 'basal_area_m2', True)
        h = number(tree['height_m'], 'height_m', True)
        comps = tree['compartments']
        if not isinstance(comps, list) or not comps:
            raise ValueError('At least one disjoint compartment is required')
        seen: set[str] = set()
        vw, cw, cn = [], [], []
        for comp in comps:
            cid = str(comp['compartment_id'])
            if not cid or cid in seen:
                raise ValueError('Compartment identifiers must be unique within a tree')
            seen.add(cid)
            if type(comp['woody']) is not bool:
                raise ValueError('woody must be an explicit Boolean')
            v = number(comp['green_solid_volume_m3'], 'green_solid_volume_m3')
            rho = number(comp['basic_density_Mg_m3'], 'basic_density_Mg_m3', True)
            f = number(comp['carbon_fraction'], 'carbon_fraction', True)
            if f > 1:
                raise ValueError('Carbon fraction exceeds dry-mass unity')
            c = v * rho * f
            if comp['woody']:
                vw.append(v); cw.append(c)
            else:
                cn.append(c)
        vj = math.fsum(vw)
        area.append(a); heights.append(h); volumes.append(vj)
        wood_c.append(math.fsum(cw)); rest_c.append(math.fsum(cn))
        profiles.append({'tree_id': ident, 'woody_volume_m3': vj,
                         'psi': vj / (a*h)})
    V = math.fsum(volumes)
    if V <= 0:
        raise ValueError('Positive total woody volume is required for beta and Lambda')
    a_sum = math.fsum(area)
    G = a_sum / A
    lam = math.fsum(a*h*p['psi'] for a,h,p in zip(area,heights,profiles)) / a_sum
    beta = math.fsum(wood_c) / V
    remainder = math.fsum(rest_c) / A
    total = (math.fsum(wood_c) + math.fsum(rest_c)) / A
    return dict(plot_id=record.get('plot_id', 'unspecified'),
                plot_area_ha=A, stems=len(trees), stems_per_ha=len(trees)/A,
                basal_area_m2_ha=G, mean_basal_area_m2=a_sum/len(trees),
                basal_area_weighted_Hpsi_m=lam,
                woody_volume_m3_ha=V/A, beta_MgC_m3=beta,
                remainder_carbon_MgC_ha=remainder, carbon_MgC_ha=total,
                closure_carbon_MgC_ha=beta*G*lam+remainder,
                tree_geometry=profiles,
                evidence_status='User-supplied material records; script checks arithmetic, not measurement authenticity or spatial representativeness.')


def write_csv(name: str, rows: list[dict[str, Any]]) -> None:
    with (DATA/name).open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def dump(name: str, value: Any) -> None:
    (DATA/name).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def main() -> None:
    if not __debug__:
        raise RuntimeError('Run without -O: validation assertions are required.')
    inp = json.loads((DATA/'inputs.json').read_text())['density_audit']
    cfg = json.loads((DATA/'physical_closure_inputs.json').read_text())
    rows = inp['rows']; row5 = next(r for r in rows if r['class']==5)
    high = [r for r in rows if r['class'] in (4,5)]
    targets = [('Class 5',row5['stock_pgc'],row5['area_ha']),
               ('Classes 4 and 5',math.fsum(r['stock_pgc'] for r in high),math.fsum(r['area_ha'] for r in high))]
    f = cfg['illustrative_carbon_fraction']; rho = cfg['illustrative_basic_density_Mg_m3']
    requirements = []
    for name,c,A in targets:
        dens = c*1e9/A
        v = dens/(rho*f)
        requirements.append(dict(domain=name, stock_PgC=c, area_ha=A,
            carbon_MgC_ha=dens, assumed_carbon_fraction=f, assumed_basic_density_Mg_m3=rho,
            conditional_biomass_Mg_ha=dens/f, equivalent_woody_volume_m3_ha=v,
            equivalent_layer_cm=v/100, inference='Requirement under specified uniform properties and zero remainder; not observed stand geometry'))
    r5 = requirements[0]
    basal = [dict(assumed_basal_area_m2_ha=g,
                  required_basal_weighted_Hpsi_m=r5['equivalent_woody_volume_m3_ha']/g,
                  inference='Conditional trade-off; neither basal area nor Hpsi is a recovered measurement')
             for g in cfg['illustrative_basal_area_m2_ha']]
    table=[]
    for r in requirements:
        table.append(f"{r['domain']} & {r['carbon_MgC_ha']:.2f} & {r['conditional_biomass_Mg_ha']:.2f} & {r['equivalent_woody_volume_m3_ha']:.2f} & {r['equivalent_layer_cm']:.2f} \\\\")
    (DATA/'physical_requirements_rows.tex').write_text('\n'.join(table)+'\n')
    (DATA/'basal_requirements_rows.tex').write_text('\n'.join(
        f"{r['assumed_basal_area_m2_ha']:.0f} & {r['required_basal_weighted_Hpsi_m']:.2f} \\\\" for r in basal)+'\n')
    write_csv('physical_requirements.csv',requirements)
    write_csv('basal_area_requirements.csv',basal)
    class_intervals={r['class']:r['range_mgc_ha'] for r in rows}
    ratios=[r['stock_pgc']*1e9/r['area_ha'] for r in rows]
    survivors=[]
    for perm in itertools.permutations(sorted(class_intervals)):
        if all(class_intervals[c][0] <= x <= class_intervals[c][1] and
               class_intervals[c][0] <= r['printed_density'] <= class_intervals[c][1]
               for c,x,r in zip(perm,ratios,rows)):
            survivors.append(list(perm))
    relabel = dict(permutations_tested=math.factorial(len(rows)),
        original_labels_in_source_row_order=[r['class'] for r in rows],
        admissible_assignments=survivors,
        tested_conditions='Fixed numerical rows, existing five intervals; printed means and stock/area ratios both within interval',
        unique_within_tested_model=len(survivors)==1,
        raster_or_vegetation_reassignment_confirmed=False,
        density_order=[dict(class_id=c,carbon_MgC_ha=x) for c,x in sorted(zip(survivors[0],ratios))])
    q = cfg['normalization_candidate_q']; low = next(r for r in rows if r['class']==1)
    c_low=low['stock_pgc']*1e9/low['area_ha']
    normalization=dict(q=q,effective_area_ratio=1/q,
        effective_area_increase_percent=(1/q-1)*100,
        class1_mean_from_candidate=q*c_low,class1_printed_mean=low['printed_density'],
        class1_difference_MgC_ha=low['printed_density']-q*c_low,
        rounding_half_unit_MgC_ha=.005,
        possible_area_workflow='Different area denominators, pixel weighting, planar/geodesic conventions, resampling or masks; cause not inferred from a constant ratio alone',
        projection_identified=False)
    summary=dict(class5=r5,
        class5_stock_fraction_of_feldpausch=row5['stock_pgc']/inp['feldpausch_stock_pgc'],
        class5_area_fraction_of_feldpausch=row5['area_ha']/inp['feldpausch_area_ha'],
        conditional_requirements=requirements,basal_area_tradeoffs=basal,
        low_biomass_example_Mg_ha=cfg['acalypha_total_Mg_per_plot']/cfg['acalypha_plot_area_ha'],
        physical_closure='c=beta_V*G_b*<H psi>_a + c_remainder; independent measured inputs, fixed mask and epoch',
        existing_data_status='Class-level stocks and areas only; original representative class-5 structural records not recovered',
        classes4and5_are_not_class5=True)
    dump('physical_closure_summary.json',summary)
    dump('class_label_assignments.json',relabel)
    dump('normalization_area_hypothesis.json',normalization)
    assertions=0; maxres=0.
    def check(condition: bool) -> None:
        nonlocal assertions
        assertions+=1
        if not condition: raise AssertionError('Physical closure diagnostic assertion '+str(assertions))
    def close(a: float,b: float) -> None:
        nonlocal maxres
        maxres=max(maxres,abs(a-b));check(math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-10))
    check(survivors==[[5,4,3,2,1]])
    close(summary['low_biomass_example_Mg_ha'],147.8)
    check(abs(normalization['class1_difference_MgC_ha'])<.005)
    check(r5['carbon_MgC_ha']>requirements[1]['carbon_MgC_ha'])
    check(round(r5['carbon_MgC_ha'],2)==536.33)
    check(round(r5['equivalent_woody_volume_m3_ha'],2)==1901.86)
    rng=random.Random(cfg['test_seed'])
    for ncase in range(cfg['randomized_cases']):
        trees=[]
        for j in range(rng.randint(2,15)):
            cs=[]
            for k in range(3):
                cs.append(dict(compartment_id=f'o{k}',woody=k<2,
                    green_solid_volume_m3=rng.uniform(.01,8),
                    basic_density_Mg_m3=rng.uniform(.15,.95),carbon_fraction=rng.uniform(.39,.53)))
            trees.append(dict(tree_id=f't{j}',basal_area_m2=rng.uniform(.01,.7),
                              height_m=rng.uniform(2,55),compartments=cs))
        rec=dict(plot_id='SYNTHETIC',plot_area_ha=rng.uniform(.1,3),trees=trees)
        z=plot_closure(rec)
        close(z['carbon_MgC_ha'],z['closure_carbon_MgC_ha'])
        close(z['basal_area_m2_ha']*z['basal_area_weighted_Hpsi_m'],z['woody_volume_m3_ha'])
        close(z['basal_area_m2_ha'],z['stems_per_ha']*z['mean_basal_area_m2'])
        mult=rng.uniform(.5,3)
        rec2=json.loads(json.dumps(rec)); rec2['plot_area_ha']*=mult
        z2=plot_closure(rec2)
        close(z2['carbon_MgC_ha']*mult,z['carbon_MgC_ha'])
        close(z2['basal_area_weighted_Hpsi_m'],z['basal_area_weighted_Hpsi_m'])
        # Two plots demonstrate why area-weighted products are needed.
        p=rng.random()
        independent_mean=p*z['carbon_MgC_ha']+(1-p)*z2['carbon_MgC_ha']
        weighted_closure=p*z['closure_carbon_MgC_ha']+(1-p)*z2['closure_carbon_MgC_ha']
        close(independent_mean,weighted_closure)
    invalid_cases=[{'plot_area_ha':0,'trees':[]},{'plot_area_ha':1,'trees':[]}]
    valid=dict(plot_area_ha=1,trees=[dict(tree_id='one',basal_area_m2=.1,height_m=10,
        compartments=[dict(compartment_id='wood',woody=True,green_solid_volume_m3=1,
            basic_density_Mg_m3=.6,carbon_fraction=.47)])])
    for key,value in [('carbon_fraction',1.2),('green_solid_volume_m3',-1),('basic_density_Mg_m3',0)]:
        x=json.loads(json.dumps(valid));x['trees'][0]['compartments'][0][key]=value;invalid_cases.append(x)
    duplicate=json.loads(json.dumps(valid));duplicate['trees']*=2;invalid_cases.append(duplicate)
    for invalid in invalid_cases:
        rejected=False
        try: plot_closure(invalid)
        except (ValueError,KeyError,TypeError): rejected=True
        check(rejected)
    # Product-of-means substitution is not a stand average.
    direct=(.2*40*20+.4*80*30)/2
    meanproduct=((.2+.4)/2)*((40+80)/2)*((20+30)/2)
    check(not math.isclose(direct,meanproduct))
    dump('stand_closure_validation.json',dict(status='PASS',seed=cfg['test_seed'],
        randomized_cases=cfg['randomized_cases'],assertions=assertions,
        maximum_absolute_arithmetic_residual=maxres,
        absolute_tolerance=1e-10,relative_tolerance=1e-12,
        scope='Synthetic closure and exact published-input diagnostics; no observed stand structure or field validation',
        all_permutations_enumerated=120))
    print(f'Physical-closure programme: {assertions} assertions; {cfg["randomized_cases"]} synthetic plots; 120 class-label permutations.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--measurements',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if args.measurements:
        if not args.output:parser.error('--output required for measurements')
        dataset=json.loads(args.measurements.read_text(encoding='utf-8'))
        if not dataset.get('plots'):parser.error('No measured plots provided')
        results=[plot_closure(p) for p in dataset['plots']]
        args.output.write_text(json.dumps({'plots':results,'status':'ARITHMETIC_CHECK_ONLY'},indent=2,allow_nan=False)+'\n')
    else:
        main()
