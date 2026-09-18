#!/usr/bin/env python3
"""Reproduce all derived numerical tables and test the analytical identities.

Python >=3.9; standard library only; no network, fitted model, or external data.
Run from any directory. Outputs are deterministic and include no runtime date.
Random checks test algebra, not empirical plausibility or forest measurements.
"""
from __future__ import annotations
import csv
import json
import math
import random
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'

def finite_vector(v: Sequence[float], name: str, positive: bool=False) -> list[float]:
    a = [float(x) for x in v]
    if not a or any(not math.isfinite(x) for x in a):
        raise ValueError(f'{name}: nonempty finite vector required')
    if any(x <= 0 if positive else x < 0 for x in a):
        raise ValueError(f'{name}: invalid sign')
    return a

def transfer(c: Sequence[float], r: Sequence[float], w: Sequence[float]) -> dict[str,float]:
    c, r, w = finite_vector(c,'stocks',True),finite_vector(r,'corrections'),finite_vector(w,'weights')
    if not len(c)==len(r)==len(w):
        raise ValueError('Vectors must have identical lengths')
    cs=math.fsum(c); mu=[x/cs for x in c]
    ew=math.fsum(p*x for p,x in zip(mu,w))
    if ew<=0: raise ValueError('Positive baseline flux required')
    rc=math.fsum(p*x for p,x in zip(mu,r))
    cov=math.fsum(p*(x-rc)*(y-ew) for p,x,y in zip(mu,r,w))
    rf=math.fsum(x*y*z for x,y,z in zip(c,r,w))/math.fsum(x*y for x,y in zip(c,w))
    vr=math.fsum(p*(x-rc)**2 for p,x in zip(mu,r))
    vw=math.fsum(p*(x-ew)**2 for p,x in zip(mu,w))
    return dict(r_stock=rc,r_flux=rf,mean_weight=ew,covariance=cov,
                bound=math.sqrt(vr*vw)/ew,stock_total=cs,
                baseline_flux=math.fsum(x*y for x,y in zip(c,w)))

def regrowth(area: Sequence[float], c0: Sequence[float], c1: Sequence[float],
             r0: Sequence[float], r1: Sequence[float], dt: float=1.0) -> dict[str, object]:
    """Finite-interval live-carbon increments. Initial zero stocks are retained.

    Positive baseline increments supply the averaging weights. Corrections on
    zero baseline increments are an additive component, not dropped units.
    Revised increments may be signed; sign reversals require separate accounting.
    """
    area=finite_vector(area,'areas',True)
    c0,c1=finite_vector(c0,'initial carbon'),finite_vector(c1,'final carbon')
    r0,r1=finite_vector(r0,'initial correction'),finite_vector(r1,'final correction')
    if len({len(v) for v in (area,c0,c1,r0,r1)})!=1:
        raise ValueError('Regrowth vectors must have equal lengths')
    if not math.isfinite(dt) or dt<=0:
        raise ValueError('Positive finite census interval required')
    g=[(b-a)/dt for a,b in zip(c0,c1)]
    if any(v<0 for v in g):
        raise ValueError('Split baseline losses from positive regrowth increments')
    gs=[(b*t-a*s)/dt for a,b,s,t in zip(c0,c1,r0,r1)]
    base=math.fsum(a*v for a,v in zip(area,g))
    new=math.fsum(a*v for a,v in zip(area,gs))
    additive=math.fsum(a*v for a,b,v in zip(area,g,gs) if b==0)
    weighted=math.fsum(a*v for a,b,v in zip(area,g,gs) if b>0)
    return dict(baseline_gain=base,revised_gain=new,zero_increment_component=additive,
                positive_increment_component=weighted,
                multiplier=new/base if base>0 else None,
                gain_weighted_factor=weighted/base if base>0 else None)

def quadratic_calibration(x: float, alpha: float) -> float:
    if not math.isfinite(x) or not math.isfinite(alpha) or x<0 or alpha<0:
        raise ValueError('Nonnegative finite mass and alpha required')
    return x*(1+alpha*x)

def write_csv(name: str, rows: list[dict]) -> None:
    with (DATA/name).open('w',encoding='utf-8',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)

def dump(name: str, obj: dict) -> None:
    (DATA/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')

def main() -> None:
    if not __debug__:
        raise RuntimeError('Run without -O: analytical checks must not be disabled.')
    inp=json.loads((DATA/'inputs.json').read_text(encoding='utf-8'))
    h=inp['historical']; s=h['baseline_share']; hist=[]
    for base in h['comparison_stocks_pgc']:
        r=h['stock_pgc']/base
        hist.append(dict(comparison_stock_pgc=base,stock_ratio=r,
          fixed_total_percent=100*s*r,
          retained_others_percent=100*s*r/(1+s*(r-1)),
          hypothetical_total_gtco2e=h['ecofys_total_gtco2e']*(1+s*(r-1))))
    d=inp['density_audit']; f=d['carbon_fraction_for_conversion']; density=[]
    for row in d['rows']:
        c=row['stock_pgc']*1e9/row['area_ha']; lo,hi=row['range_mgc_ha']
        density.append(dict(class_id=row['class'],area_ha=row['area_ha'],stock_pgc=row['stock_pgc'],
          carbon_density_mgc_ha=c,dry_agb_mg_ha=c/f,printed_density_mgc_ha=row['printed_density'],
          ratio_within_printed_interval=lo<=c<=hi,
          printed_density_within_printed_interval=lo<=row['printed_density']<=hi))
    high=[r for r in d['rows'] if r['class'] in (4,5)]
    high_area=math.fsum(r['area_ha'] for r in high); high_stock=math.fsum(r['stock_pgc'] for r in high)
    mean=d['reported_total_stock_pgc']*1e9/d['reported_total_area_ha']
    overview=dict(total_area_ha=d['reported_total_area_ha'],total_stock_pgc=d['reported_total_stock_pgc'],
      carbon_density_mgc_ha=mean,dry_agb_mg_ha=mean/f,
      dry_agb_sensitivity_mg_ha=sorted(mean/x for x in d['carbon_fraction_sensitivity']),
      high_classes_area_ha=high_area,high_classes_stock_pgc=high_stock,
      high_classes_carbon_density_mgc_ha=high_stock*1e9/high_area,
      high_classes_dry_agb_mg_ha=high_stock*1e9/high_area/f,
      row_stock_sum_pgc=math.fsum(r['stock_pgc'] for r in d['rows']),
      row_area_sum_ha=math.fsum(r['area_ha'] for r in d['rows']),
      domain_area_ratio_to_feldpausch=d['reported_total_area_ha']/d['feldpausch_area_ha'])
    reference_density=d['feldpausch_stock_pgc']*1e9/d['feldpausch_area_ha']
    overview.update(feldpausch_density_mgc_ha=reference_density,
      mixed_domain_density_ratio=mean/reference_density,
      high_class_density_ratio=overview['high_classes_carbon_density_mgc_ha']/reference_density,
      high_class_stock_ratio=high_stock/d['feldpausch_stock_pgc'],
      high_class_area_ratio=high_area/d['feldpausch_area_ha'])
    support=[]
    for name,a,c in [('Feldpausch forest mask',d['feldpausch_area_ha'],d['feldpausch_stock_pgc']),
                     ('Historical mixed domain',d['reported_total_area_ha'],d['reported_total_stock_pgc']),
                     ('Historical classes 4 and 5',high_area,high_stock)]:
        support.append(dict(domain=name,area_mha=a/1e6,stock_pgc=c,density_mgc_ha=c*1e9/a,
          area_ratio_to_feldpausch=a/d['feldpausch_area_ha'],
          density_ratio_to_feldpausch=c*1e9/a/reference_density,
          stock_ratio_to_feldpausch=c/d['feldpausch_stock_pgc']))
    rows_by_class={r['class']:r for r in d['rows']}; swap=[]
    for cls,other in [(2,3),(3,2)]:
        row=rows_by_class[cls];lo,hi=rows_by_class[other]['range_mgc_ha']
        ratio=row['stock_pgc']*1e9/row['area_ha']
        swap.append(dict(class_id=cls,recalculated_density=ratio,
           own_interval=','.join(map(str,row['range_mgc_ha'])),
           other_class=other,other_interval=','.join(map(str,[lo,hi])),
           fits_other_interval=lo<=ratio<=hi,
           printed_density_fits_other_interval=lo<=row['printed_density']<=hi,
           correction_confirmed=False))
    rg=[]
    for case in inp['regrowth_cases']:
        z=regrowth(case['area_ha'],case['c0'],case['c1'],case['r0'],case['r1'],case['dt_years'])
        rg.append(dict(case=case['case'],**z))
    se=inp['size_calibration_example'];a=se['alpha'];m=lambda v:quadratic_calibration(v,a)
    n=se['survivor_count'];x0,x1,xd=se['survivor_initial'],se['survivor_final'],se['dead_initial']
    G=n*(x1-x0);L=xd;GG=n*(m(x1)-m(x0));LL=m(xd)
    size=[]
    for name,rG,rL in [('Loss-weighted hypothesis',se['hypothesis_case_gain_factor'],se['hypothesis_case_loss_factor']),
                      ('Increasing-size counterexample',GG/G,LL/L)]:
        size.append(dict(case=name,baseline_gain=G,baseline_loss=L,baseline_net=G-L,
          gain_multiplier=rG,loss_multiplier=rL,revised_gain=rG*G,revised_loss=rL*L,
          revised_net=rG*G-rL*L,common_gain_scaled_net=rG*(G-L),
          differential_penalty=(rL-rG)*L))
    p=inp['synthetic_paired']; F,U,O=p['forest_source'],p['forest_removal'],p['other_sources']; paired=[]
    for x in p['cases']:
        fs=F*x['r_source']; us=U*x['r_removal']; net=fs-us; total=O+net
        paired.append(dict(case=x['case'],r_source=x['r_source'],r_removal=x['r_removal'],
          forest_source=fs,forest_removal=us,forest_net=net,total_net=total,
          gross_source_share_percent=100*fs/(O+fs),net_forest_share_percent=100*net/total))
    examples=[transfer([50,50],[1,3],w) for w in ([.02,0],[0,.02])]
    setting=inp['validation']; rng=random.Random(setting['seed'])
    at,rt=setting['absolute_tolerance'],setting['relative_tolerance']
    errors={k:0.0 for k in ['transfer','paired_covariance','uniform_net','differential_net','census','regrowth_increment','regrowth_aggregation','support_decomposition','size_growth_factor','census_differential','bias_conversion']}
    assertions=0
    def check(name: str, a: float,b: float) -> None:
        nonlocal assertions
        residual=abs(a-b); errors[name]=max(errors[name],residual);assertions+=1
        if not math.isclose(a,b,abs_tol=at,rel_tol=rt):
            raise AssertionError(f'{name}: {a} != {b}, residual {residual}')
    for _ in range(setting['cases']):
        n=rng.randrange(2,21); c=[rng.uniform(.1,100) for _ in range(n)]
        rr=[rng.uniform(.1,4) for _ in range(n)]
        wp=[rng.uniform(.001,.2) for _ in range(n)]; wm=[rng.uniform(.001,.2) for _ in range(n)]
        plus,minus=transfer(c,rr,wp),transfer(c,rr,wm)
        for q in (plus,minus):
            check('transfer',q['r_flux'],q['r_stock']+q['covariance']/q['mean_weight'])
            assertions+=2
            assert min(rr)-at <= q['r_flux'] <= max(rr)+at
            assert abs(q['r_flux']-q['r_stock'])<=q['bound']+at
        fs,us=plus['baseline_flux'],minus['baseline_flux']
        netstar=plus['r_flux']*fs-minus['r_flux']*us
        check('paired_covariance',netstar-(fs-us),(plus['r_stock']-1)*(fs-us)+plus['stock_total']*(plus['covariance']-minus['covariance']))
        scale=rng.uniform(.1,4)
        check('uniform_net',scale*fs-scale*us,scale*(fs-us))
        delta=rng.uniform(-.1,.1)
        check('differential_net',(scale+delta/2)*fs-(scale-delta/2)*us,scale*(fs-us)+delta*(fs+us)/2)
        c0,c1,r0,r1=[rng.uniform(.1,10) for _ in range(4)]
        check('census',r1*c1-r0*c0,r0*(c1-c0)+c1*(r1-r0))
        # Increment-based regrowth: retain a zero starting stock in every case.
        areas=[rng.uniform(.1,10) for _ in range(n)]
        cg0=[0.0]+[rng.uniform(0,100) for _ in range(n-1)]
        cg1=[v+rng.uniform(.1,10) for v in cg0]
        dt=rng.uniform(.1,5);rr0=[rng.uniform(.5,2) for _ in range(n)]
        rr1=[rng.uniform(.5,2) for _ in range(n)]
        zz=regrowth(areas,cg0,cg1,rr0,rr1,dt)
        direct=math.fsum(A*(b*t-c*s)/dt for A,c,b,s,t in zip(areas,cg0,cg1,rr0,rr1))
        expanded=math.fsum(A*(s*(b-c)+b*(t-s))/dt for A,c,b,s,t in zip(areas,cg0,cg1,rr0,rr1))
        check('regrowth_increment',direct,expanded)
        check('regrowth_aggregation',zz['revised_gain'],zz['positive_increment_component']+zz['zero_increment_component'])
        # Stable, nonlinear size correction: growth uses a secant, loss a level.
        alpha=rng.uniform(0,.01);xx0=rng.uniform(.1,100);xx1=xx0+rng.uniform(.1,20)
        qg=(quadratic_calibration(xx1,alpha)-quadratic_calibration(xx0,alpha))/(xx1-xx0)
        check('size_growth_factor',qg,1+alpha*(xx0+xx1))
        gain,loss=rng.uniform(.1,100),rng.uniform(.1,100);rgain,rloss=rng.uniform(.5,3),rng.uniform(.5,3)
        check('census_differential',rgain*gain-rloss*loss,rgain*(gain-loss)-(rloss-rgain)*loss)
    bad=[([],[],[]),([1],[1],[0]),([1],[1,2],[.1]),([0],[1],[.1]),([1],[float('nan')],[.1]),([1],[1],[-1])]
    for args in bad:
        try: transfer(*args)
        except ValueError: assertions+=1
        else: raise AssertionError(f'Invalid input accepted: {args}')
    # Explicit regression tests, including the source-table contradictions.
    assert [r['class_id'] for r in density if not r['ratio_within_printed_interval']]==[2,3]
    assert math.isclose(examples[0]['r_flux'],1) and math.isclose(examples[1]['r_flux'],3)
    assert math.isclose(paired[2]['forest_net'],.5,abs_tol=at)
    assert paired[3]['forest_net']<0
    assert math.isclose(overview['row_stock_sum_pgc'],723.95,abs_tol=at)
    assertions+=5
    # Exact cancellation is not evidence of small gross flows.
    assert math.isclose(2.5*6-2.5*6,0,abs_tol=at); assertions+=1
    for row in support:
        check('support_decomposition',row['stock_ratio_to_feldpausch'],
              row['area_ratio_to_feldpausch']*row['density_ratio_to_feldpausch'])
    assert all(row['fits_other_interval'] and row['printed_density_fits_other_interval'] for row in swap)
    assert not any(row['correction_confirmed'] for row in swap)
    assert math.isclose(rg[0]['baseline_gain'],5) and math.isclose(rg[0]['revised_gain'],6)
    assert math.isclose(rg[1]['revised_gain'],17) and math.isclose(rg[1]['zero_increment_component'],5)
    assert math.isclose(size[0]['revised_net'],-6) and math.isclose(size[1]['revised_net'],72)
    assert xd>x1 and size[1]['gain_multiplier']>size[1]['loss_multiplier']
    assert regrowth([1],[0],[0],[1],[1])['multiplier'] is None
    assertions+=7
    for args in [([1],[1],[0],[1],[1]),([1],[0],[1],[1],[1],0),([1],[0],[1],[1,2],[1])]:
        try:regrowth(*args)
        except ValueError:assertions+=1
        else:raise AssertionError('Invalid regrowth input accepted')
    gv=inp['gonzalez_validation'];bias_factors=[]
    for b in gv['allometric_bias_percent']:
        factor=1/(1+b/100);bias_factors.append(factor)
        check('bias_conversion',factor*(1+b/100),1)
    assert gv['calibration_trees']+gv['validation_trees']==gv['sample_total_trees'];assertions+=1
    validation=dict(status='PASS',revision_date=inp['revision_date'],seed=setting['seed'],
      randomized_cases=setting['cases'],assertions=assertions,
      absolute_tolerance=at,relative_tolerance=rt,max_absolute_residuals=errors,
      evidence_status='Numerical algebra checks only; not empirical validation.')
    calc=dict(revision_date=inp['revision_date'],historical=hist,
      ecofys_implied_component_gtco2=h['baseline_share']*h['ecofys_total_gtco2e'],
      density_summary=overview,paired_examples=paired,
      cancellation_ratio=abs(F-U)/(F+U),two_unit_examples=examples,
      harvest_bias_replacement_factors=bias_factors,
      support_comparison=support,interval_swap_diagnostic=swap,
      regrowth_examples=rg,size_differential_examples=size)
    from extensions import extend
    calc,validation,extra_macros=extend(DATA,inp,calc,validation,transfer)
    from audit_extensions import extend_audit
    calc,validation=extend_audit(DATA,inp,calc,validation)
    assertions=validation['assertions']
    dump('calculations.json',calc);dump('validation.json',validation)
    write_csv('historical_calculations.csv',hist);write_csv('density_audit.csv',density);write_csv('paired_source_sink.csv',paired)
    write_csv('support_comparison.csv',support);write_csv('interval_swap_diagnostic.csv',swap)
    write_csv('regrowth_examples.csv',rg);write_csv('census_differential.csv',size)
    # Typeset tables are generated from the very same values, preventing drift.
    rows=[]
    for x,src in zip(density,inp['density_audit']['rows']):
        lo,hi=src['range_mgc_ha']
        rows.append(f"{x['class_id']} & {lo}--{hi} & {x['area_ha']/1e6:.3f} & {x['stock_pgc']:.2f} & {x['printed_density_mgc_ha']:.2f} & {x['carbon_density_mgc_ha']:.2f} & {src['printed_percentage']} "+r"\\")
    (DATA/'density_rows.tex').write_text('\n'.join(rows)+'\n')
    rows=[f"{x['comparison_stock_pgc']:.1f} & {x['stock_ratio']:.5f} & {x['fixed_total_percent']:.2f} & {x['retained_others_percent']:.2f} \\\\" for x in hist]
    (DATA/'historical_rows.tex').write_text('\n'.join(rows)+'\n')
    rows=[f"{x['case']} & {x['r_source']:.1f} & {x['r_removal']:.1f} & {x['forest_source']:.2f} & {x['forest_removal']:.2f} & {x['forest_net']:.2f} & {x['gross_source_share_percent']:.2f} & {x['net_forest_share_percent']:.2f} \\\\" for x in paired]
    (DATA/'paired_rows.tex').write_text('\n'.join(rows)+'\n')
    size_rows=[f"{x['case']} & {x['gain_multiplier']:.2f} & {x['loss_multiplier']:.2f} & {x['revised_gain']:.1f} & {x['revised_loss']:.1f} & {x['revised_net']:.1f} " + r"\\" for x in size]
    (DATA/'census_rows.tex').write_text('\n'.join(size_rows)+'\n')
    macros={'MeanCarbon' :f'{mean:.2f}','MeanBiomass':f'{mean/f:.2f}',
      'HighBiomass':f"{overview['high_classes_dry_agb_mg_ha']:.2f}",
      'FeldDensity':f'{reference_density:.2f}','MixedDensityRatio':f"{overview['mixed_domain_density_ratio']:.3f}",'HighDensityRatio':f"{overview['high_class_density_ratio']:.3f}",'HighStockRatio':f"{overview['high_class_stock_ratio']:.3f}",'HighAreaRatio':f"{overview['high_class_area_ratio']:.3f}",'TestAssertions':str(assertions),'TestCases':str(setting['cases'])}
    macros.update(extra_macros)
    (DATA/'derived.tex').write_text('\n'.join('\\newcommand{\\'+k+'}{'+v+'}' for k,v in macros.items())+'\n')
    print(json.dumps(validation,indent=2)); print('Regenerated numerical audit, census and cohort outputs.')

if __name__=='__main__':
    main()
    from measurement_evidence import main as reproduce_measurement_evidence
    reproduce_measurement_evidence()

    from population_atmosphere import main as reproduce_population_atmosphere
    reproduce_population_atmosphere()

    from physical_closure import main as reproduce_physical_closure
    reproduce_physical_closure()

    from class5_comparison import main as reproduce_class5_comparison
    reproduce_class5_comparison()

if __name__ == "__main__":
    from admissibility import main as additional_checks
    additional_checks()
