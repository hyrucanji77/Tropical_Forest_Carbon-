#!/usr/bin/env python3
"""Version-4 numerical audits and exact census/timing checks; standard library.

The event examples are synthetic. A numerical exclusion at a finite set of
exponents is not a proof over a continuum of calibration exponents.
"""
from __future__ import annotations
import csv
import math
import random
from pathlib import Path
from typing import Sequence


def events(x0: Sequence[float], x1: Sequence[float], deaths: Sequence[float]):
    x0, x1, deaths = list(map(float,x0)), list(map(float,x1)), list(map(float,deaths))
    if not x0 or len(x0)!=len(x1) or not deaths:
        raise ValueError('Matched nonempty gain intervals and deaths are required')
    if any(not math.isfinite(x) or x<0 for x in x0+x1+deaths):
        raise ValueError('Finite nonnegative stocks required')
    if any(y<=x for x,y in zip(x0,x1)) or any(x<=0 for x in deaths):
        raise ValueError('Separate zero or negative gain events; mortality must be positive')
    gains=[y-x for x,y in zip(x0,x1)]
    return x0,x1,deaths,gains,math.fsum(gains),math.fsum(deaths)


def quadratic_census(x0, x1, deaths, alpha=1.0, k=.005):
    if not math.isfinite(alpha) or not math.isfinite(k) or alpha<=0 or k<0:
        raise ValueError('alpha>0 and k>=0 must be finite')
    x0,x1,deaths,g,G,L=events(x0,x1,deaths)
    mean_g=math.fsum(t*(x+y)/2 for t,x,y in zip(g,x0,x1))/G
    mean_l=math.fsum(x*x for x in deaths)/L
    new_g=math.fsum(alpha*(y-x)+k*(y*y-x*x) for x,y in zip(x0,x1))
    new_l=math.fsum(alpha*x+k*x*x for x in deaths)
    return dict(gain_factor=new_g/G,loss_factor=new_l/L,
                gain_mean_midpoint=mean_g,loss_mean_stock=mean_l,
                difference=(new_l/L-new_g/G),criterion=k*(mean_l-2*mean_g),
                arithmetic_size_ratio=mean_l/mean_g)


def power_increment(x0:float,x1:float,b:float)->float:
    """Stable x1**b-x0**b for positive intervals, including recruitment from zero."""
    if x0==0:return x1**b
    return x0**b*math.expm1(b*math.log1p((x1-x0)/x0))


def power_census(x0,x1,deaths,a=1.0,b=1.5):
    if not math.isfinite(a) or not math.isfinite(b) or a<=0 or b<=1:
        raise ValueError('a>0, b>1 must be finite; b=1 has equal scale factors')
    x0,x1,deaths,g,G,L=events(x0,x1,deaths)
    p=b-1
    moment_l=math.fsum(x*x**p for x in deaths)/L
    moment_g=math.fsum(power_increment(x,y,b)/b for x,y in zip(x0,x1))/G
    # Log ratio avoids division of nearly equal powered means near b=1.
    log_ratio=(math.log(moment_l)-math.log(moment_g))/p
    log_threshold=math.log1p(p)/p
    return dict(exponent=b,gain_factor=a*b*moment_g,loss_factor=a*moment_l,
                gain_power_moment=moment_g,loss_power_moment=moment_l,
                log_power_mean_ratio=log_ratio,log_threshold=log_threshold,
                power_mean_ratio=math.exp(log_ratio),threshold=math.exp(log_threshold),
                difference=a*(moment_l-b*moment_g))


def save_csv(folder:Path,name:str,rows:list[dict])->None:
    with (folder/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def extend(data:Path,inp:dict,calc:dict,validation:dict,transfer):
    settings=inp['extended_validation'];rng=random.Random(settings['seed'])
    at,rt=inp['validation']['absolute_tolerance'],inp['validation']['relative_tolerance']
    errors={k:0. for k in ['quadratic_exact','quadratic_scale','power_exact','power_scale',
                          'power_quadratic_equivalence','opposite_order','cumulative_recovery',
                          'late_release']}
    count=0
    def check(key,x,y):
        nonlocal count
        count+=1;errors[key]=max(errors[key],abs(x-y))
        if not math.isclose(x,y,abs_tol=at,rel_tol=rt):
            raise AssertionError(f'{key}: {x} != {y}')
    def truth(condition,message):
        nonlocal count
        count+=1
        if not condition:raise AssertionError(message)
    for ncase in range(settings['cases']):
        n=rng.randrange(2,13);nd=rng.randrange(1,8)
        xx0=[rng.uniform(.1,500) for _ in range(n)]
        if ncase%3==0:xx0[0]=0.
        xx1=[v+rng.uniform(.1,30) for v in xx0]
        dead=[rng.uniform(.1,600) for _ in range(nd)]
        alpha=rng.uniform(.2,2.5);k=rng.uniform(.0001,.01)
        q=quadratic_census(xx0,xx1,dead,alpha,k)
        check('quadratic_exact',q['difference'],q['criterion'])
        q2=quadratic_census(xx0,xx1,dead,alpha+1,k)
        check('quadratic_scale',q2['difference'],q['difference'])
        b=rng.uniform(1.01,2);a=rng.uniform(.2,2.5)
        z=power_census(xx0,xx1,dead,a,b)
        gain=math.fsum(y-x for x,y in zip(xx0,xx1));loss=math.fsum(dead)
        direct_g=a*math.fsum(y**b-x**b for x,y in zip(xx0,xx1))/gain
        direct_l=a*math.fsum(x**b for x in dead)/loss
        check('power_exact',z['gain_factor'],direct_g)
        check('power_exact',z['loss_factor'],direct_l)
        check('power_exact',z['difference'],direct_l-direct_g)
        z2=power_census(xx0,xx1,dead,a*2,b)
        check('power_scale',z2['difference'],z['difference']*2)
        truth((z['difference']>0)==(z['log_power_mean_ratio']>z['log_threshold']),
              'Exponent-specific direction test failed')
        zquad=power_census(xx0,xx1,dead,1,2)
        check('power_quadratic_equivalence',zquad['difference'],q['loss_mean_stock']-2*q['gain_mean_midpoint'])
        # A finite cohort: ranks are deliberately opposite; no empirical claim.
        stocks=[rng.uniform(1,100) for _ in range(n)]
        corr=sorted(rng.uniform(.5,3) for _ in range(n))
        first=sorted([rng.uniform(.01,.95) for _ in range(n)],reverse=True)
        init=transfer(stocks,corr,first);later=transfer(stocks,corr,[1-w for w in first])
        truth(init['r_flux']<=init['r_stock']+at,'Opposite-order sign failed')
        mu=[c/math.fsum(stocks) for c in stocks]
        pair=.5*math.fsum(mu[i]*mu[j]*(corr[i]-corr[j])*(first[i]-first[j]) for i in range(n) for j in range(n))
        check('opposite_order',pair,init['covariance'])
        lifetime=transfer(stocks,corr,[1.]*n)
        check('cumulative_recovery',lifetime['r_flux'],init['r_stock'])
        combined=(init['r_flux']*init['baseline_flux']+later['r_flux']*later['baseline_flux'])/math.fsum(stocks)
        check('late_release',combined,init['r_stock'])
    # Shared normalisation inferred only from displayed values and rounding.
    norm=[]
    for row in inp['density_audit']['rows']:
        m,A,C=row['printed_density'],row['area_ha'],row['stock_pgc']
        q=m*A/(C*1e9)
        low=(m-.005)*(A-.005)/((C+.005)*1e9)
        high=(m+.005)*(A+.005)/((C-.005)*1e9)
        norm.append(dict(class_id=row['class'],printed_to_recalculated_ratio=q,
                         factor_lower=low,factor_upper=high,
                         effective_denominator_multiplier=1/q,
                         exact_one_percent_denominator_compatible=low<=1/1.01<=high))
    low=max(r['factor_lower'] for r in norm);high=min(r['factor_upper'] for r in norm)
    truth(low<=high,'Common-factor intersection absent')
    common=(low+high)/2
    for row in norm:truth(row['factor_lower']<=common<=row['factor_upper'],'Common factor fails row')
    truth(not (low<=1/1.01<=high),'Exact 1.01 factor unexpectedly compatible')
    # Explicit finite-interval counterexample to an arithmetic universal screen.
    ce=inp['power_screen_counterexample'];xx0=ce['initial'];xx1=ce['final'];dd=ce['deaths']
    qc=quadratic_census(xx0,xx1,dd,1,.005);pc=power_census(xx0,xx1,dd,1,1.5)
    truth(qc['arithmetic_size_ratio']<2 and pc['difference']>0,'Power-screen counterexample failed')
    truth(qc['difference']<0,'Quadratic screen direction failed')
    criteria=[]
    for label,rr in [('quadratic',qc),('power b=1.5',pc)]:
        criteria.append(dict(family=label,gain_factor=rr['gain_factor'],loss_factor=rr['loss_factor'],difference=rr['difference'],arithmetic_size_ratio=qc['arithmetic_size_ratio'],status='synthetic exact event calculation'))
    thresholds=[dict(b=b,threshold=math.exp(math.log(b)/(b-1))) for b in [1.0001,1.01,1.1,1.25,1.5,1.75,2.]]
    truth(all(x['threshold']>y['threshold'] for x,y in zip(thresholds,thresholds[1:])),'Threshold monotonicity failed')
    t=inp['timing_example'];timing=[]
    for name,weights in [('Initial year',t['first_fractions']),('Later combined',[1-v for v in t['first_fractions']]),('Lifetime',[1.]*len(t['stocks']) )]:
        z=transfer(t['stocks'],t['corrections'],weights)
        timing.append(dict(period=name,baseline_release=z['baseline_flux'],corrected_release=z['baseline_flux']*z['r_flux'],stock_multiplier=z['r_stock'],release_multiplier=z['r_flux'],covariance=z['covariance']))
    truth(math.isclose(timing[0]['release_multiplier'],55/45),'Timing regression failed')
    fractions=[]
    for f in [.4111,.4999,.47,.50]:
        fractions.append(dict(fraction=f,mixed_domain_biomass=calc['density_summary']['carbon_density_mgc_ha']/f,high_class_biomass=calc['density_summary']['high_classes_carbon_density_mgc_ha']/f,status='sensitivity; measured-range applicability to mapped domain is conditional'))
    for function,args in [
      (quadratic_census,([],[],[1])),(quadratic_census,([1],[1],[1])),
      (quadratic_census,([1],[2],[0])),(quadratic_census,([0],[1],[1],0,.1)),
      (power_census,([1],[2],[1],1,1)),(power_census,([float('nan')],[2],[1])),
      (power_census,([1],[0],[1])),(power_census,([1],[2],[-1]))]:
        try:function(*args)
        except ValueError:count+=1
        else:raise AssertionError('Invalid event/calibration inputs accepted')
    extension=dict(seed=settings['seed'],randomized_cases=settings['cases'],assertions=count,max_absolute_residuals=errors,
                   normalization_intersection=[low,high],normalization_cause_confirmed=False,
                   exact_one_percent_denominator_compatible=False,
                   arithmetic_prescreen_counterexample=dict(quadratic=qc,power=pc),
                   exact_power_criterion='Finite-interval growth distribution; not a midpoint approximation')
    validation['baseline_assertions']=validation['assertions']
    validation['assertions']+=count;validation['extended_tests']=extension
    validation['randomized_cases_total']=validation['randomized_cases']+settings['cases']
    calc.update(normalization_diagnostic=norm,normalization_intersection=[low,high],
                carbon_fraction_sensitivity=fractions,exact_census_criteria=criteria,
                power_thresholds=thresholds,timing_example=timing,edgar_land_reference=inp['edgar_land'])
    for name,rows in [('normalization_diagnostic.csv',norm),('carbon_fraction_sensitivity.csv',fractions),
                      ('census_criteria.csv',criteria),('power_thresholds.csv',thresholds),
                      ('timing_examples.csv',timing),('edgar_land_reference.csv',inp['edgar_land'])]:save_csv(data,name,rows)
    return calc,validation,{'ExtendedCases':str(settings['cases'])}
