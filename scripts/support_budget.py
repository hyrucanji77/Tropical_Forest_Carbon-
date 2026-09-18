#!/usr/bin/env python3
"""Sharp bounded-moment cap tests and process-resolved GCB accounting.

Standard library only. Quoted decimals are parsed as exact rational inputs.
Random checks test formulas, not empirical forests. No raster, field records,
empirical calibration error or geographic exposure fractions are inferred.
"""
from __future__ import annotations
import csv
import json
import math
import random
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'

def q(x):
    return x if isinstance(x, Q) else Q(str(x))

def cap_bounds(lower, threshold, upper, mean, area):
    a,t,b,m,A = map(q, (lower, threshold, upper, mean, area))
    if not (a < t < b and a <= m <= b and A > 0):
        raise ValueError('Require lower < threshold < upper, mean inside support, positive area.')
    # Valid for all means in the class, with the upper-bound proof based on convexity.
    frac_min = max(Q(0), (m-t)/(b-t))
    loss_min = max(Q(0), m-t)
    loss_max = (b-t)*(m-a)/(b-a)
    return dict(min_area_fraction=frac_min, min_area_ha=A*frac_min,
                cap_mean_min=loss_min, cap_mean_max=loss_max,
                cap_stock_min_PgC=A*loss_min/Q(10**9),
                cap_stock_max_PgC=A*loss_max/Q(10**9))

def dump(name,obj):
    (DATA/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')

def csvwrite(name,rows):
    with (DATA/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)

def main():
    src=json.loads((DATA/'support_budget_inputs.json').read_text())
    c,g=src['class5'],src['gcb']; assertions=0; max_err=0.
    def check(cond):
        nonlocal assertions
        assertions += 1
        if not cond: raise AssertionError(f'Support/budget check {assertions} failed')
    def close(a,b):
        nonlocal max_err
        a,b=float(a),float(b);max_err=max(max_err,abs(a-b))
        check(math.isclose(a,b,abs_tol=1e-10,rel_tol=1e-12))
    A=q(c['area_ha']);a=q(c['interval_lower_MgC_ha']);b=q(c['interval_upper_MgC_ha'])
    means=[('Stock-area ratio',q(c['stock_PgC'])*10**9/A),('Printed mean',q(c['printed_mean_MgC_ha']))]
    total=q(c['pantropical_reported_total_PgC']);rows=[]
    for t_s in [c['reported_response_endpoint_MgC_ha'],c['regional_value_p22_MgC_ha']]:
        t=q(t_s)
        for convention,m in means:
            z=cap_bounds(a,t,b,m,A)
            row={'mean_convention':convention,'threshold_MgC_ha':float(t),'mean_MgC_ha':float(m),
                 'minimum_exceeding_area_percent':float(100*z['min_area_fraction']),
                 'minimum_exceeding_area_Mha':float(z['min_area_ha']/10**6),
                 'cap_change_min_PgC':float(z['cap_stock_min_PgC']),
                 'cap_change_max_PgC':float(z['cap_stock_max_PgC']),
                 'cap_min_percent_reported_total':float(100*z['cap_stock_min_PgC']/total),
                 'cap_max_percent_reported_total':float(100*z['cap_stock_max_PgC']/total),
                 'status':'Conditional bounded-moment cap calculation; not an empirical error bound'}
            rows.append(row)
            # Exact equality cases prove sharpness under the assumptions.
            p=z['min_area_fraction'];check((1-p)*t+p*b == m)
            check(p*(b-t) == z['cap_mean_min'])
            pb=(m-a)/(b-a);check((1-pb)*a+pb*b==m)
            check(pb*(b-t) == z['cap_mean_max'])
            check(z['cap_mean_min'] <= z['cap_mean_max'])
            # All cells may exceed the threshold, despite the minimum area bound.
            check(m>t and max(m-t,0)==z['cap_mean_min'])
    # Check numbers directly against rational inputs, not manuscript rounded labels.
    close(rows[0]['mean_MgC_ha'],536.3257329758882)
    check(all(r['cap_max_percent_reported_total']<3 for r in rows))
    for invalid in [(478,478,605,536,1),(478,606,605,536,1),(478,523,605,606,1),(478,523,605,536,0)]:
        try:cap_bounds(*invalid)
        except (ValueError,ZeroDivisionError):check(True)
        else:check(False)
    rng=random.Random(src['validation']['seed'])
    for _ in range(src['validation']['cases']):
        n=rng.randrange(2,30)
        xs=[rng.uniform(float(a),float(b)) for _ in range(n)]
        ws=[rng.uniform(.001,1) for _ in xs];norm=math.fsum(ws);ws=[v/norm for v in ws]
        t=rng.uniform(float(a)+.01,float(b)-.01)
        m=math.fsum(w*x for w,x in zip(ws,xs));p=math.fsum(w for w,x in zip(ws,xs) if x>t)
        d=math.fsum(w*max(x-t,0) for w,x in zip(ws,xs))
        z=cap_bounds(a,t,b,m,A)
        check(p+1e-12 >= float(z['min_area_fraction']))
        check(d+1e-10 >= float(z['cap_mean_min']))
        check(d-1e-10 <= float(z['cap_mean_max']))
        close(m-math.fsum(w*min(x,t) for w,x in zip(ws,xs)),d)
        # Region-specific recalibration of a selected pair.
        F,U=[rng.uniform(.01,10) for _ in range(2)];pF,pU=rng.random(),rng.random();r=rng.uniform(.1,4)
        Fs=F*((1-pF)+pF*r);Us=U*((1-pU)+pU*r)
        close((Fs-Us)-(F-U),(r-1)*(pF*F-pU*U))
    # A cap does not bound true error in the in-range response labels.
    check(max(Q(500)-523,0)==0);check(Q(500)-300==200)
    csvwrite('support_tail_bounds.csv',rows)
    (DATA/'support_tail_rows.tex').write_text('\n'.join(
        f"{r['mean_convention']} & {r['minimum_exceeding_area_percent']:.2f} & {r['minimum_exceeding_area_Mha']:.1f} & {r['cap_change_min_PgC']:.2f}--{r['cap_change_max_PgC']:.2f} & {r['cap_max_percent_reported_total']:.2f} "+r'\\'
        for r in rows if r['threshold_MgC_ha']==523)+'\n')
    fs=[q(c['carbon_fraction_min']),q(c['carbon_fraction_max'])]
    tissues=[]
    for name,m in [('Class-5 lower edge',a)]+means:
        tissues.append({'density_convention':name,'carbon_MgC_ha':float(m),
                        'minimum_dry_biomass_Mg_ha':float(m/fs[1]),
                        'maximum_dry_biomass_Mg_ha':float(m/fs[0]),
                        'condition':'All compartment fractions contained in reported tissue range'})
        check(m/fs[1]<=m/fs[0]);close(float(m/fs[1])*float(fs[1]),m)
    csvwrite('support_tissue_bounds.csv',tissues)
    F,U=q(g['deforestation_total_GtC_yr']),q(g['regrowth_total_GtC_yr'])
    Fp,Up=q(g['permanent_deforestation_GtC_yr']),q(g['reafforestation_removal_GtC_yr'])
    Fs,Us=F-Fp,U-Up;delta=q(g['illustrative_differential_delta']);pairs=[]
    for name,f,u,origin in [('Selected total',F,U,'Rounded source totals'),('Permanent change',Fp,Up,'Rounded source components'),('Shifting cultivation',Fs,Us,'Differences of rounded source totals and components')]:
        pairs.append({'process_pair':name,'period':g['period'],'source_GtC_yr':float(f),'removal_GtC_yr':float(u),
                      'net_GtC_yr':float(f-u),'gross_sum_GtC_yr':float(f+u),'eta':float(abs(f-u)/(f+u)),
                      'source_GtCO2_yr':float(f*Q(44,12)),'removal_GtCO2_yr':float(u*Q(44,12)),
                      'shift_at_delta_0_1_GtC_yr':float(delta*(f+u)/2),'origin':origin})
    check(Fp+Fs==F and Up+Us==U);check((Fp-Up)+(Fs-Us)==F-U)
    close(pairs[0]['eta'],.1875);close(pairs[1]['eta'],5/17);close(pairs[2]['eta'],1/15)
    close(pairs[1]['shift_at_delta_0_1_GtC_yr']+pairs[2]['shift_at_delta_0_1_GtC_yr'],.16)
    r=q(g['illustrative_common_multiplier']);source_only=(r-1)*Fp;both=(r-1)*(Fp-Up)
    check(source_only==Q('0.22'));check(both==Q('0.10'))
    check(q(g['china_usa_eu27_reafforestation_removal_GtC_yr'])/Up==Q('0.5'))
    csvwrite('gcb_process_components.csv',pairs)
    (DATA/'gcb_process_rows.tex').write_text('\n'.join(f"{x['process_pair']} & {x['source_GtC_yr']:.1f} & {x['removal_GtC_yr']:.1f} & {x['net_GtC_yr']:.1f} & {x['eta']:.2f} & {x['shift_at_delta_0_1_GtC_yr']:.3f} "+r'\\' for x in pairs)+'\n')
    years=g['cumulative_period_end']-g['cumulative_period_start']+1
    base=q(g['reported_cumulative_imbalance_GtC']);add=q(g['illustrative_persistent_source_GtC_yr'])*years
    check(years==66);check(add==33);check(base+add==68)
    scenarios=[{'scenario':'Reported rounded baseline','period':'1959-2024','source_increment_GtC':0.,'other_net_adjustment_GtC':0.,'imbalance_GtC':float(base)},
               {'scenario':'Extra 0.5 GtC/yr; other terms fixed','period':'1959-2024','source_increment_GtC':float(add),'other_net_adjustment_GtC':0.,'imbalance_GtC':float(base+add)},
               {'scenario':'Retain baseline residual','period':'1959-2024','source_increment_GtC':float(add),'other_net_adjustment_GtC':float(-add),'imbalance_GtC':float(base)},
               {'scenario':'Close constructed account to zero','period':'1959-2024','source_increment_GtC':float(add),'other_net_adjustment_GtC':float(-(base+add)),'imbalance_GtC':0.}]
    for row in scenarios:close(base+q(row['source_increment_GtC'])+q(row['other_net_adjustment_GtC']),row['imbalance_GtC'])
    csvwrite('multiyear_budget_scenarios.csv',scenarios)
    reg=q(c['regional_architecture_mean_MgC_ha'])/q(c['regional_allometric_mean_MgC_ha'])
    close(reg,2.8827552515876893)
    dump('support_budget_summary.json',{'edition':'7.2','class5_bounds':rows,'biomass_bounds':tissues,
         'regional_preprint_ratio_of_displayed_means':float(reg),'gcb_pairs':pairs,
         'permanent_source_only_example_GtC_yr':float(source_only),'permanent_both_exposed_example_GtC_yr':float(both),
         'multiyear_scenarios':scenarios,'cumulative_residual_fraction_of_530':float(base/q(g['reported_cumulative_emissions_GtC'])),
         'no_empirical_calibration_error_inferred':True,'no_geographic_flux_fractions_inferred':True})
    dump('support_budget_validation.json',{'status':'PASS','assertions':assertions,'seed':src['validation']['seed'],
         'randomized_cases':src['validation']['cases'],'maximum_absolute_identity_residual':max_err,
         'absolute_tolerance':1e-10,'relative_tolerance':1e-12,
         'scope':'Exact printed-input bounds, source decomposition and synthetic checks; not empirical validation'})
    print(f'Support and process-budget checks: {assertions} PASS')

if __name__=='__main__':main()
