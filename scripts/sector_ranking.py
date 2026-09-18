#!/usr/bin/env python3
"""Conditional sector ranking on the explicitly retained 2010 Ecofys grouping.

This is an accounting reconstruction, not a fitted annual land-use correction.
No empirical transfer from the arXiv stock ratios to the Ecofys component is
established by these calculations. All output tables use the same inputs.
"""
from pathlib import Path
import csv, json, math, random
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'

def retained_account(total, component, land_remainder, other_sectors, multiplier):
    vals=[total, component, land_remainder, multiplier,*other_sectors]
    if any(not math.isfinite(v) for v in vals):raise ValueError('Finite values required')
    if total<=0 or component<=0 or multiplier<0 or land_remainder<0 or not other_sectors or any(v<0 for v in other_sectors):raise ValueError('Invalid positive-source partition')
    if not math.isclose(component+land_remainder+sum(other_sectors),total,rel_tol=1e-12,abs_tol=1e-10):raise ValueError('Partition does not close')
    revised_total=total+(multiplier-1)*component
    land=multiplier*component+land_remainder
    if revised_total<=0:raise ValueError('Revised denominator must be positive')
    threshold=(max(other_sectors)-land_remainder)/component
    return {'revised_total':revised_total,'revised_land_group':land,
            'land_share':land/revised_total,'other_shares':[x/revised_total for x in other_sectors],
            'largest':land>max(other_sectors),'threshold':threshold}

def main():
    inp=json.loads((DATA/'sector_ranking_inputs.json').read_text())
    T=inp['reference_total_gtco2e']; f=T*inp['land_component_share']; a=T*inp['retained_land_group_share']; industry=T*inp['industry_share']
    # The remaining source sum is a residual of displayed data, not a new sector.
    remainder=T-f-a-industry
    rows=[]
    for S in inp['comparison_stocks_pgc']:
        r=inp['arxiv_stock_pgc']/S
        z=1+(r-1)*inp['land_component_share']
        L=r*f+a
        rows.append(dict(comparison_stock_pgc=S,imposed_component_multiplier=r,
             component_percent_original_total=100*r*f/T,
             land_group_percent_original_total=100*L/T,
             revised_total_gtco2e=T*z,revised_land_group_gtco2e=L,
             unchanged_industry_gtco2e=industry,
             land_group_percent_revised_total=100*L/(T*z),
             industry_percent_revised_total=100*industry/(T*z),
             land_group_exceeds_industry=L>industry,
             component_alone_exceeds_industry=r*f>industry))
    def dump(name,obj):(DATA/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
    with (DATA/'historical_sector_ranking.csv').open('w',newline='') as out:
        w=csv.DictWriter(out,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    tex=[]
    for row in rows:
        tex.append(f"{row['comparison_stock_pgc']:.1f} & {row['component_percent_original_total']:.2f} & {row['land_group_percent_original_total']:.2f} & {row['revised_total_gtco2e']:.2f} & {row['land_group_percent_revised_total']:.2f} & {row['industry_percent_revised_total']:.2f} "+r'\\')
    (DATA/'historical_ranking_rows.tex').write_text('\n'.join(tex)+'\n')
    threshold=(inp['industry_share']-inp['retained_land_group_share'])/inp['land_component_share']
    component_threshold=inp['industry_share']/inp['land_component_share']
    dump('sector_ranking_summary.json',dict(rows=rows,land_group_multiplier_threshold=threshold,
        component_alone_multiplier_threshold=component_threshold,
        category_scope=inp['category_scope'],evidence_status=inp['evidence_status'],
        conclusion='Both imposed multiplier endpoints make the historical Ecofys land-use group the largest sector; the component alone does not rank first at the lower endpoint.',
        energy_supersector_claim=False,contemporary_lulucf_measurement=False))
    rng=random.Random(20260918); assertions=0
    for _ in range(1000):
        f=rng.uniform(.01,20);a=rng.uniform(0,10);others=[rng.uniform(.01,20) for _ in range(7)];T=f+a+sum(others);r=rng.uniform(.2,8)
        x=retained_account(T,f,a,others,r)
        assert math.isclose(x['revised_land_group']+sum(others),x['revised_total'],rel_tol=1e-12);assertions+=1
        assert math.isclose(x['land_share']+sum(x['other_shares']),1,rel_tol=1e-12);assertions+=1
        assert x['largest']==(r>x['threshold']);assertions+=1
        assert x['largest']==(x['land_share']>max(x['other_shares']));assertions+=1
        # Renormalization cannot change ordering of unchanged sectors.
        assert (others[0]>others[1])==(x['other_shares'][0]>x['other_shares'][1]);assertions+=1
        if r>=1:
            assert x['revised_total']>=T;assertions+=1
    assert rows[0]['land_group_exceeds_industry'] and rows[1]['land_group_exceeds_industry'];assertions+=1
    assert not rows[0]['component_alone_exceeds_industry'] and rows[1]['component_alone_exceeds_industry'];assertions+=1
    assert round(rows[0]['revised_total_gtco2e'],2)==56.34 and round(rows[1]['revised_total_gtco2e'],2)==59.48;assertions+=1
    assert math.isclose(threshold,2.3980582524271847);assertions+=1
    dump('sector_ranking_validation.json',dict(status='PASS',seed=20260918,randomized_cases=1000,assertions=assertions,
        empirical_validation=False,scope='Accounting identities, ranking invariance and historical scenario regression.'))
    print(f'Conditional sector-ranking checks: PASS; {assertions} assertions.')
if __name__=='__main__':main()
