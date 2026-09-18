#!/usr/bin/env python3
"""Reproduce published intermediate-stem aggregates and transparent account examples.

Python >=3.9; standard library; no network. These calculations distinguish
reported model outputs from physical observations and synthetic mass balances.
"""
from __future__ import annotations
import csv
import json
import math
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / 'data'


def carbon_stock(n: float, biomass: float, fraction: float) -> float:
    if not all(math.isfinite(x) for x in (n, biomass, fraction)):
        raise ValueError('Finite inputs required')
    if n < 0 or biomass < 0 or not 0 <= fraction <= 1:
        raise ValueError('Nonnegative count and mass; carbon fraction in [0,1]')
    return n * biomass * fraction


def write_json(name: str, value: object) -> None:
    (DATA / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def main() -> None:
    if not __debug__:
        raise RuntimeError('Run without -O: validation assertions are required')
    inp = json.loads((DATA / 'population_atmosphere_inputs.json').read_text())
    s=inp['intermediate_class']; n=s['stems_per_plot_basis']
    if n<=0: raise ValueError('Positive denominator for per-stem means')
    mean_b=s['biomass_tonnes_per_plot_basis']*1000/n
    mean_c=s['carbon_tonnes_per_plot_basis']*1000/n
    result={'source':s['source'], 'dbh_class_cm':s['dbh_class_cm'],
      'mean_biomass_kg_per_stem_derived':mean_b,
      'mean_carbon_kg_per_stem_derived':mean_c,
      'biomass_share_percent_source_reported':s['biomass_share_percent_reported'],
      'carbon_share_percent_source_reported':s['carbon_share_percent_reported'],
      'combined_II_III_biomass_share_percent_source_reported':s['combined_II_III_biomass_share_percent_reported'],
      'interpretation':'Ratio of displayed class aggregates, not a fixed individual mass or a pantropical threshold.',
      'architectural_records':inp['architectural_records']}
    abundance=[]
    for row in inp['synthetic_abundance']:
        c=carbon_stock(row['stems'],row['biomass_kg_per_stem'],row['carbon_fraction'])
        released=c*row['affected_fraction']*row['first_year_release_fraction']
        abundance.append(dict(row, standing_carbon_kg=c, first_year_release_kgC=released,
                              first_year_release_kgCO2=released*44/12))
    cases=[]
    for row in inp['synthetic_annual_accounts']:
        f=row['forest_release'];o=math.fsum(row['other_sources']);u=row['land_removal']+row['ocean_removal']
        cases.append({'case':row['case'],'forest_release':f,'other_source_sum':o,
          'source_total':f+o,'removal_sum':u,'atmospheric_increment':f+o-u,
          'forest_is_largest_source':f>max(row['other_sources']),
          'forest_is_majority_source':f>o})
    b=cases[0]
    for case in cases:
        case['atmospheric_increment_difference_from_baseline']=case['atmospheric_increment']-b['atmospheric_increment']
    delay=inp['delay_example'];releases=[delay['omitted_carbon']*p for p in delay['annual_release_fractions']]
    retained=[x*delay['assumed_airborne_retention_fraction'] for x in releases]
    result.update(synthetic_abundance=abundance,synthetic_annual_accounts=cases,
                  synthetic_delay={'release_by_year':releases,'prescribed_retained_carbon_by_year':retained,
                    'cumulative_release':math.fsum(releases),'cumulative_retained':math.fsum(retained),
                    'status':'Illustration with prescribed retention, not a measured atmospheric response'})
    checks=[]
    def check(name, condition):
        assert condition, name
        checks.append(name)
    check('biomass mean 96 kg',mean_b==96)
    check('carbon mean separate',math.isclose(mean_c,1300/30))
    check('biomass is not carbon',mean_b>mean_c)
    check('table class limits',s['dbh_class_cm']==[10,30])
    check('class share reported',s['biomass_share_percent_reported']==38.97)
    check('carbon share reported',s['carbon_share_percent_reported']==38.79)
    check('combined smaller-class share',math.isclose(38.97+23.74,62.71))
    check('majority community contribution',s['combined_II_III_biomass_share_percent_reported']>50)
    check('three original records',len(inp['architectural_records'])==3)
    for row in inp['architectural_records']:
        check(row['taxon']+' within reported near-100 range',100<row['aboveground_biomass_kg']<120)
        check(row['taxon']+' below20cm',row['dbh_cm']<20)
    check('intermediate population stock greater',abundance[0]['standing_carbon_kg']>abundance[1]['standing_carbon_kg'])
    check('intermediate population release greater',abundance[0]['first_year_release_kgC']>abundance[1]['first_year_release_kgC'])
    check('smaller individual',abundance[0]['biomass_kg_per_stem']<abundance[1]['biomass_kg_per_stem'])
    for c in cases:
        check(c['case']+' balance',math.isclose(c['source_total']-c['removal_sum'],c['atmospheric_increment']))
    check('omitted source increases accumulation',cases[1]['atmospheric_increment_difference_from_baseline']==1)
    check('reallocation preserves accumulation',cases[2]['atmospheric_increment_difference_from_baseline']==0)
    check('explicit extra sink preserves accumulation',cases[3]['atmospheric_increment_difference_from_baseline']==0)
    check('forest correction alone insufficient for leading',not cases[1]['forest_is_largest_source'])
    check('leading does not require majority',cases[4]['forest_is_largest_source'] and not cases[4]['forest_is_majority_source'])
    check('majority implies leading',cases[5]['forest_is_majority_source'] and cases[5]['forest_is_largest_source'])
    check('reduced uptake adds atmospheric effect',cases[6]['atmospheric_increment_difference_from_baseline']==1.5)
    check('delay conserves carbon',math.isclose(math.fsum(releases),10))
    check('all delayed releases positive',all(x>0 for x in releases))
    check('retention model stated separately',math.isclose(math.fsum(retained),5))
    check('no automatic full airborne retention',math.fsum(retained)<math.fsum(releases))
    for args in [(-1,100,.5),(1,-100,.5),(1,100,1.1),(1,100,float('nan'))]:
        try:carbon_stock(*args)
        except ValueError: check('reject '+str(args),True)
        else:raise AssertionError('invalid input accepted')
    write_json('population_atmosphere_summary.json',result)
    write_json('population_atmosphere_validation.json',{'status':'PASS','deterministic_checks':len(checks),
      'checks':checks,'scope':'Transcription regressions and algebraic examples; no new inventory or atmospheric fit.'})
    with (DATA/'atmospheric_account_examples.csv').open('w',newline='',encoding='utf-8') as f:
        wr=csv.DictWriter(f,fieldnames=list(cases[0]));wr.writeheader();wr.writerows(cases)
    table=[
      ('Stems per 0.05 ha','30','Reported'),
      ('Biomass (tonnes per 0.05 ha)','2.88','Reported'),
      ('Carbon (tonnes C per 0.05 ha)','1.30','Reported'),
      ('Share of community biomass (\\%)','38.97','Reported'),
      ('Share of community carbon (\\%)','38.79','Reported'),
      ('Mean biomass per stem (kg)',f'{mean_b:.2f}','Derived'),
      ('Mean carbon per stem (kgC)',f'{mean_c:.2f}','Derived'),
      ('Classes II + III biomass share (\\%)','62.71','Reported')]
    (DATA/'intermediate_stem_rows.tex').write_text('\n'.join(' & '.join(row)+r' \\' for row in table)+'\n')
    print('Population and atmospheric examples: PASS;',len(checks),'deterministic checks.')

if __name__=='__main__': main()
