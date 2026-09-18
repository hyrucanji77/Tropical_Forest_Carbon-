#!/usr/bin/env python3
"""Exact stem/branch identities and explicitly conditional account scenarios.

All randomly generated objects are synthetic numerical tests. No class-5 tree
measurements, distributional upper bounds, or empirical bias estimates are fitted.
The module uses only Python's standard library and writes deterministic outputs.
"""
from __future__ import annotations
import csv
import io
import json
import math
import random
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'


def positive(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise ValueError(name + ' must be finite and strictly positive')
    return value


def psi_from_mass(stem_ratio: float, branch_mass_fraction: float,
                  density_ratio: float = 1.0) -> float:
    f = positive(stem_ratio, 'stem_ratio')
    k = positive(density_ratio, 'density_ratio')
    q = float(branch_mass_fraction)
    if not math.isfinite(q) or not 0 <= q < 1:
        raise ValueError('branch_mass_fraction must lie in [0,1)')
    return f * (1.0 + k * q / (1.0 - q))


def carbon_envelope(beta_max: float, cylinders_max: float, stem_ratio_max: float,
                    branch_volume_fraction_max: float, remainder_max: float = 0.0) -> float:
    beta = positive(beta_max, 'beta_max')
    cylinders = positive(cylinders_max, 'cylinders_max')
    f = positive(stem_ratio_max, 'stem_ratio_max')
    q = float(branch_volume_fraction_max)
    r = float(remainder_max)
    if not math.isfinite(q) or not 0 <= q < 1:
        raise ValueError('branch volume fraction bound must lie in [0,1)')
    if not math.isfinite(r) or r < 0:
        raise ValueError('remainder bound must be finite and nonnegative')
    return beta * cylinders * f / (1 - q) + r


def csv_write(name: str, records: list[dict[str, Any]]) -> None:
    out = io.StringIO(newline='')
    writer = csv.DictWriter(out, fieldnames=list(records[0]), lineterminator='\n')
    writer.writeheader()
    writer.writerows(records)
    (DATA / name).write_text(out.getvalue(), encoding='utf-8')


def main() -> None:
    if not __debug__:
        raise RuntimeError('Run numerical validation without Python -O.')
    inp = json.loads((DATA / 'structural_constraints_inputs.json').read_text(encoding='utf-8'))
    carbon = inp['stock_pgc'] * 1e9 / inp['area_ha']
    beta = inp['illustrative_basic_density'] * inp['illustrative_carbon_fraction']
    volume = carbon / beta
    q = inp['simplified_branch_fraction']
    flo, fhi = inp['illustrative_stem_ratio']
    scenarios = []
    for g, h in inp['basal_area_height_scenarios']:
        cylinder = g * h
        psi = volume / cylinder
        scenarios.append(dict(
            basal_area_m2_per_ha=g, basal_area_weighted_height_m=h,
            cylinder_volume_m3_per_ha=cylinder,
            required_whole_wood_ratio=psi,
            scenario_whole_wood_ratio_min=psi_from_mass(flo,q),
            scenario_whole_wood_ratio_max=psi_from_mass(fhi,q),
            scenario_carbon_min_mgc_per_ha=beta*cylinder*psi_from_mass(flo,q),
            scenario_carbon_max_mgc_per_ha=beta*cylinder*psi_from_mass(fhi,q),
            required_branch_to_stem_volume_min=psi/fhi-1,
            required_branch_to_stem_volume_max=psi/flo-1,
            required_stem_ratio_at_branch_fraction=psi*(1-q),
            empirical_status='specified sensitivity scenario; not an observed stand'))
    csv_write('form_factor_scenarios.csv', scenarios)
    rows=[]
    for s in scenarios:
        rows.append(f"{s['basal_area_m2_per_ha']:.0f} & {s['basal_area_weighted_height_m']:.0f} & "
                    f"{s['cylinder_volume_m3_per_ha']:,.0f} & {s['required_whole_wood_ratio']:.2f} & "
                    f"{s['scenario_carbon_min_mgc_per_ha']:.0f}--{s['scenario_carbon_max_mgc_per_ha']:.0f} " + r'\\')
    (DATA/'form_factor_rows.tex').write_text('\n'.join(rows)+'\n',encoding='utf-8')

    fossil = inp['gcb_2024_fossil_gtc_per_year']
    net_land = inp['gcb_2024_net_land_gtc_per_year']
    sigma = inp['gcb_2024_fossil_standard_uncertainty']
    boundary = (fossil-net_land)/2
    attribution = [dict(
        account='2024 two-source net CO2 partition; fixed sum and removals',
        fossil_baseline_gtc_per_year=fossil,
        net_land_baseline_gtc_per_year=net_land,
        reassignment_strictly_above_gtc_per_year=boundary,
        fossil_cutoff_fraction=boundary/fossil,
        standard_uncertainty_multiples=boundary/sigma,
        probability_interpretation='none; uncertainty is not a hard bound or assumed Gaussian')]
    csv_write('attribution_thresholds.csv',attribution)

    mean_q = (0.20+0.68)/2
    psi_mean = (psi_from_mass(0.5,0.20)+psi_from_mass(0.5,0.68))/2
    summary = dict(
        edition='7.3', scope='Conditional requirements and exact algebra; no new field inventory',
        class5_carbon_mgc_per_ha=carbon, illustrative_beta_mgc_per_m3=beta,
        illustrative_wood_volume_m3_per_ha=volume,
        weighted_counterexample=dict(cylinder_weights=[0.5,0.5],stem_ratios=[0.5,0.5],
            branch_volume_fractions=[0.20,0.68],mean_fraction=mean_q,
            true_weighted_whole_wood_ratio=psi_mean,ratio_from_mean_fraction=psi_from_mass(.5,mean_q)),
        illustrative_class_bound=dict(
            positive_joint_bound_required=True, bounds_are_empirically_established=False,
            beta_max=beta,stem_ratio_max=fhi,branch_volume_fraction_max=q,remainder_max=0,
            carbon_at_cylinder_cap_1200=carbon_envelope(beta,1200,fhi,q),
            carbon_at_cylinder_cap_2000=carbon_envelope(beta,2000,fhi,q)),
        low_cylinder_branch_to_stem_range=[min(s['required_branch_to_stem_volume_min'] for s in scenarios[:2]),
                                          max(s['required_branch_to_stem_volume_max'] for s in scenarios[:2])],
        low_cylinder_branch_volume_fraction_range=[min(1-fhi/s['required_whole_wood_ratio'] for s in scenarios[:2]),
                                                 max(1-flo/s['required_whole_wood_ratio'] for s in scenarios[:2])],
        differential_example=dict(F=6,U=5.8,common_scale=1,delta=.1,
                                  baseline_net=.2,differential_net_increment=.59,corrected_net=.79))
    (DATA/'structural_admissibility.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')

    tests = 0
    max_error: dict[str,float] = {}
    def equal(a: float,b: float,family: str) -> None:
        nonlocal tests
        tests += 1
        max_error[family]=max(max_error.get(family,0.0),abs(a-b))
        if not math.isclose(a,b,abs_tol=1e-10,rel_tol=1e-12):
            raise AssertionError((family,a,b))
    def check(condition: bool) -> None:
        nonlocal tests
        tests += 1
        if not condition:
            raise AssertionError('Boolean condition failed')
    rng=random.Random(inp['test_seed'])
    for _ in range(inp['randomized_cases']):
        cylinder=rng.uniform(1,250)
        vs=rng.uniform(.01,150)
        vb=rng.uniform(0,200)
        rho_s=rng.uniform(.2,1.1)
        rho_b=rng.uniform(.2,1.1)
        f=vs/cylinder
        qv=vb/(vs+vb)
        qm=rho_b*vb/(rho_s*vs+rho_b*vb)
        psi=(vs+vb)/cylinder
        equal(psi, f/(1-qv),'volume_fraction')
        equal(psi, psi_from_mass(f,qm,rho_s/rho_b),'mass_fraction_density')
        equal(psi/f-1, vb/vs,'branch_stem_ratio')
        # Plot aggregation retains cylinder weights and material products.
        n=rng.randint(2,15)
        ks=[rng.uniform(.1,250) for _ in range(n)]
        fs=[rng.uniform(.05,.6) for _ in range(n)]
        qs=[rng.uniform(0,.44) for _ in range(n)]
        sum_volume=sum(k*ff/(1-qq) for k,ff,qq in zip(ks,fs,qs))
        equal(sum_volume/sum(ks),sum(k/sum(ks)*ff/(1-qq) for k,ff,qq in zip(ks,fs,qs)), 'weighted_plot')
        target_cylinder=rng.uniform(1,2000)
        beta_p=rng.uniform(.05,beta)
        remainder=rng.uniform(0,20)
        c=beta_p*target_cylinder*sum_volume/sum(ks)+remainder
        upper=carbon_envelope(beta,2000,.6,.44,20)
        check(c <= upper+1e-10)
        # Nonnegative physical properties assure dimensional carbon accounting.
        equal(beta_p*sum_volume, sum(beta_p*k*ff/(1-qq) for k,ff,qq in zip(ks,fs,qs)), 'carbon_sum')
        # Ranking is strict above, and reversed below, the equality threshold.
        p=rng.uniform(6,12);l=rng.uniform(.1,3)
        threshold=(p-l)/2
        dx=rng.uniform(.001,.05)
        check(l+threshold+dx > p-threshold-dx)
        check(l+threshold-dx < p-threshold+dx)
    equal(psi_mean,1.09375,'mean_counterexample')
    equal(psi_from_mass(.5,.44),.5/.56,'mean_substitution')
    check(psi_mean > psi_from_mass(.5,.44))
    equal(scenarios[0]['scenario_carbon_min_mgc_per_ha'],181.28571428571428,'printed_scenarios')
    equal(scenarios[1]['scenario_carbon_max_mgc_per_ha'],362.57142857142856,'printed_scenarios')
    check(scenarios[1]['scenario_carbon_max_mgc_per_ha'] < carbon)
    check(scenarios[2]['scenario_carbon_min_mgc_per_ha'] < carbon < scenarios[2]['scenario_carbon_max_mgc_per_ha'])
    equal(boundary,4.5,'fossil_reassignment')
    equal(boundary/sigma,9,'uncertainty_scale')
    for args in [(-1,.4,1),(.4,1,1),(.4,-.1,1),(.4,.4,0),(.4,float('nan'),1)]:
        try: psi_from_mass(*args)
        except ValueError: check(True)
        else: check(False)
    for args in [(0,1,.4,.4,0),(.2,1,.4,1,0),(.2,1,.4,.4,-1)]:
        try: carbon_envelope(*args)
        except ValueError: check(True)
        else: check(False)
    record=dict(status='PASS',seed=inp['test_seed'],randomized_cases=inp['randomized_cases'],
        assertions=tests,absolute_tolerance=1e-10,relative_tolerance=1e-12,
        max_absolute_residuals=max_error,
        scope='Synthetic algebra, specified sensitivity scenarios and source-input regression; no empirical class-5 bound')
    (DATA/'structural_constraints_validation.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(record,indent=2))

if __name__=='__main__':
    main()
