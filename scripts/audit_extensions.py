#!/usr/bin/env python3
"""Published-digit audit, cohort convolution, subset bounds and near-linear tests.

Only standard-library dependencies. Decimal intervals describe display models,
not confidence intervals. Uniform-error probabilities are conditional reference
calculations; they are not posterior probabilities of an author's workflow.
"""
from __future__ import annotations
from decimal import Decimal, localcontext, ROUND_DOWN, ROUND_HALF_UP
from fractions import Fraction
from pathlib import Path
import csv, json, math, random
D=lambda x:Decimal(str(x))

def csv_write(root:Path,name:str,rows:list[dict])->None:
    with (root/name).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def interval(value,rule):
    x=D(value); step=D('.01')
    if rule=='nearest': return x-step/2,x+step/2
    if rule=='truncation': return x,x+step
    raise ValueError('Unknown display rule')

def irwin_hall_cdf(x:Fraction,n:int)->Fraction:
    if x<=0:return Fraction(0)
    if x>=n:return Fraction(1)
    total=Fraction(0)
    for k in range(math.floor(x)+1):
        total+=(-1)**k*math.comb(n,k)*(x-k)**n
    return total/math.factorial(n)

def quantization(inp):
    rows=inp['density_audit']['rows']; total=D(inp['density_audit']['reported_total_stock_pgc'])
    norm=[];joint={};percent=[]
    for rule in ('nearest','truncation'):
        for r in rows:
            cl,ch=interval(r['stock_pgc'],rule); al,ah=interval(r['area_ha'],rule); ml,mh=interval(r['printed_density'],rule)
            lo=ml*al/(ch*D('1e9')); hi=mh*ah/(cl*D('1e9'))
            norm.append(dict(display_model=rule,class_id=r['class'],q_lower=str(lo),q_upper=str(hi),one_over_1_01_compatible=lo<=D(1)/D('1.01')<=hi))
        take=[r for r in norm if r['display_model']==rule]
        joint[rule]={'lower':str(max(D(r['q_lower']) for r in take)),'upper':str(min(D(r['q_upper']) for r in take))}
    for r in rows:
        raw=100*D(r['stock_pgc'])/total; printed=D(r['printed_percentage'])
        percent.append(dict(class_id=r['class'],source_percentage=str(printed),calculated_percentage=str(raw),truncated_percentage=str(raw.quantize(D('.01'),rounding=ROUND_DOWN)),rounded_percentage=str(raw.quantize(D('.01'),rounding=ROUND_HALF_UP))))
    fixed_denom_intersection=[max(100*D(r['stock_pgc'])/(D(r['printed_percentage'])+D('.005')) for r in rows), min(100*D(r['stock_pgc'])/(D(r['printed_percentage'])-D('.005')) for r in rows)]
    latent_numerator_intersection=[max(100*(D(r['stock_pgc'])-D('.005'))/(D(r['printed_percentage'])+D('.005')) for r in rows), min(100*(D(r['stock_pgc'])+D('.005'))/(D(r['printed_percentage'])-D('.005')) for r in rows)]
    # Independently uniform hidden fractions for five components. A positive
    # two-unit discrepancy has probability 1/120 under nearest rounding.
    truncp=irwin_hall_cdf(Fraction(3),5)-irwin_hall_cdf(Fraction(2),5)
    roundp=irwin_hall_cdf(Fraction(5),5)-irwin_hall_cdf(Fraction(4),5)
    probabilities={'assumptions':'Five components with independent uniform hidden last-digit fractions; total computed from exact component sum and displayed under the same rule; ties have zero probability.',
      'positive_two_unit_gap_truncation':{'exact':str(truncp),'decimal':float(truncp)},
      'positive_two_unit_gap_nearest':{'exact':str(roundp),'decimal':float(roundp)},
      'absolute_two_unit_gap_nearest':{'exact':str(2*roundp),'decimal':float(2*roundp)},
      'interpretation':'Conditional diagnostic only. Stock and area displays are not assumed independent; probabilities are not multiplied.'}
    endpoints=[];slo=D(0);shi=D(1)
    for base,published in zip(inp['historical']['comparison_stocks_pgc'],['26.15','32.60']):
        ratio=total/D(base); x=100*D('.103')*ratio
        endpoints.append(dict(comparison_stock=str(base),fixed_share_full=str(x),truncated=str(x.quantize(D('.01'),rounding=ROUND_DOWN)),rounded=str(x.quantize(D('.01'),rounding=ROUND_HALF_UP)),published=published))
        slo=max(slo,(D(published)-D('.005'))/(100*ratio));shi=min(shi,(D(published)+D('.005'))/(100*ratio))
    stock_gap=total-sum(D(r['stock_pgc']) for r in rows)
    area_gap=D(inp['density_audit']['reported_total_area_ha'])-sum(D(r['area_ha']) for r in rows)
    return {'normalization':norm,'joint':joint,'percentages':percent,'nearest_percentage_denominator_fixed_numerators':{'bounds':[str(x) for x in fixed_denom_intersection],'feasible':fixed_denom_intersection[0]<fixed_denom_intersection[1]},
       'nearest_percentage_denominator_with_rounded_numerators':{'bounds':[str(x) for x in latent_numerator_intersection],'feasible':latent_numerator_intersection[0]<latent_numerator_intersection[1],'interpretation':'Even with half-unit latent stock uncertainty the exact joint intersection is empty by about 0.000026 PgC; a value near 724.08 is only approximate, not a compatible exact solution.'},
       'sum_gaps':{'stock_pgc':str(stock_gap),'area_ha':str(area_gap)},'gap_probabilities':probabilities,
       'historical_endpoints':endpoints,'baseline_share_interval_nearest':[str(slo),str(shi)],
       'causal_display_rule_confirmed':False}

def annual(c,r,kernels,history):
    if len(c)!=len(r) or len(kernels)!=len(c) or not history: raise ValueError('shape mismatch')
    if any(len(p)!=len(history) for p in kernels):raise ValueError('lag mismatch')
    if any(not math.isfinite(v) or v<0 for row in kernels for v in row):raise ValueError('invalid kernel')
    if any(not math.isfinite(v) or v<0 for v in history):raise ValueError('invalid history')
    weights=[math.fsum(d*p for d,p in zip(history,k)) for k in kernels]
    f=math.fsum(x*w for x,w in zip(c,weights))
    if f<=0:raise ValueError('positive release needed')
    fc=math.fsum(x*y*w for x,y,w in zip(c,r,weights))
    return {'baseline':f,'corrected':fc,'multiplier':fc/f,'weights':weights}

def log_primitive(x):return 0.0 if x==0 else x*(math.log(x)-1)

def extend_audit(data:Path,inp:dict,calc:dict,validation:dict):
    checks=0; rng=random.Random(20260918); maxerr={'annual':0.0,'nearlinear_scaled_remainder':0.0}
    def check(ok,message):
        nonlocal checks
        checks+=1
        if not ok:raise AssertionError(message)
    with localcontext() as ctx:
        ctx.prec=60; q=quantization(inp)
    check(all(x['truncated_percentage']==x['source_percentage'] for x in q['percentages']),'percentage truncation')
    for model in ('nearest','truncation'):
        check(D(q['joint'][model]['lower'])<D(q['joint'][model]['upper']),'empty common q')
        excludes=[x['class_id'] for x in q['normalization'] if x['display_model']==model and not x['one_over_1_01_compatible']]
        check(excludes==[5,4],'1.01 exclusions changed')
    check(q['gap_probabilities']['positive_two_unit_gap_truncation']['exact']=='11/20','truncation probability')
    check(q['gap_probabilities']['positive_two_unit_gap_nearest']['exact']=='1/120','one-sided rounding probability')
    check(all(x['truncated']==x['published'] for x in q['historical_endpoints']),'historical truncation')
    rows=[]
    for name,h in [('Constant clearing',[1.,1.]),('Latest doubled',[2.,1.]),('Latest halved',[.5,1.])]:
        z=annual([50.,50.],[1.,3.],[[.8,.2],[.1,.9]],h)
        rows.append(dict(scenario=name,latest_activity=h[0],previous_activity=h[1],baseline_release=z['baseline'],corrected_release=z['corrected'],annual_multiplier=z['multiplier']))
    for row,expected in zip(rows,[2.,51/29,69/31]):check(math.isclose(row['annual_multiplier'],expected,rel_tol=1e-14),'annual regression')
    # General stationary mixtures and exact two-lag sign under opposite order.
    for _ in range(1000):
        n=rng.randint(2,12);c=[rng.uniform(.1,30) for _ in range(n)];r=sorted(rng.uniform(.2,4) for _ in range(n));p=sorted((rng.uniform(.01,.99) for _ in range(n)),reverse=True)
        hist=[rng.uniform(.1,4),rng.uniform(.1,4)];z=annual(c,r,[[v,1-v] for v in p],hist)
        s=sum(c);mu=[v/s for v in c];rc=sum(a*b for a,b in zip(mu,r)); ep=sum(a*b for a,b in zip(mu,p));cov=sum(a*(b-rc)*(v-ep) for a,b,v in zip(mu,r,p))
        expected=rc+(hist[0]-hist[1])*cov/(hist[1]+(hist[0]-hist[1])*ep)
        err=abs(expected-z['multiplier']);maxerr['annual']=max(maxerr['annual'],err)
        check(math.isclose(expected,z['multiplier'],abs_tol=1e-12,rel_tol=1e-12),'annual identity')
        check((z['multiplier']-rc)*(hist[0]-hist[1])<=1e-10,'two-lag sign')
        kernel=[]
        for i in range(n):
            v=[rng.random() for _ in range(4)];ss=sum(v);kernel.append([a/ss for a in v])
        zz=annual(c,r,kernel,[2.]*4)
        check(math.isclose(zz['multiplier'],rc,abs_tol=1e-12),'stationary complete cohorts')
    # Near-linear derivatives: logs use an explicit reference stock x*=1.
    near=[]
    for case in range(100):
        lo=[0.0]+[rng.uniform(.1,20) for _ in range(4)];hi=[x+rng.uniform(.1,3) for x in lo];dead=[rng.uniform(.1,30) for _ in range(4)]; a=1.3
        G=sum(b-v for v,b in zip(lo,hi)); L=sum(dead)
        logsL=sum(x*math.log(x) for x in dead)/L
        logsG=sum(log_primitive(b)-log_primitive(v) for v,b in zip(lo,hi))/G
        coefficient=a*(logsL-logsG-1)
        eps=D('.000001')
        with localcontext() as ctx:
            ctx.prec=60; b=D(1)+eps
            gd=sum(D(y)**b-(D(x)**b if x else D(0)) for x,y in zip(lo,hi))/sum(D(y)-D(x) for x,y in zip(lo,hi))
            ld=sum(D(x)**b for x in dead)/sum(D(x) for x in dead)
            exact=float(D(a)*(ld-gd)); rem=abs(exact-float(eps)*coefficient)/(float(eps)**2)
        maxerr['nearlinear_scaled_remainder']=max(maxerr['nearlinear_scaled_remainder'],rem)
        check(rem<1000,'near-linear expansion convergence')
        if case<3:near.append(dict(case=case,epsilon=str(eps),exact_difference=exact,first_order=float(eps)*coefficient,coefficient=coefficient,loss_log_mean=logsL,gain_log_mean=logsG))
    # Conditional subset lower bound and the extra condition for a finite bracket.
    A=inp['density_audit']['feldpausch_area_ha'];C=inp['density_audit']['feldpausch_stock_pgc'];high=calc['density_summary'];HC=high['high_classes_stock_pgc'];HA=high['high_classes_area_ha']; cd=C*1e9/A
    bound=HC/C; benchmark=HC/(HA*cd/1e9)
    scenarios=[]
    for multiplier in [.5,1,1.2]:
        local_density=cd*multiplier; local_stock=HA*local_density/1e9; ratio=HC/local_stock
        scenarios.append(dict(conventional_local_density_mgc_ha=local_density,conventional_subset_stock_pgc=local_stock,required_stock_factor=ratio))
        check(local_stock<=C and ratio>=bound,'conditional lower bound')
    check(scenarios[0]['required_stock_factor']>benchmark,'no unconditional upper bound')
    for args in [([1],[2],[[1]],[-1]),([1],[2],[[1,0]],[1]),([1],[2],[[0]],[1])]:
        try:annual(*args)
        except ValueError:checks+=1
        else:raise AssertionError('invalid annual input accepted')
    # Save exact digit intervals as strings to retain precision in the audit.
    (data/'display_precision_audit.json').write_text(json.dumps(q,indent=2)+'\n')
    csv_write(data,'display_model_normalization.csv',q['normalization']);csv_write(data,'printed_percentage_audit.csv',q['percentages']);csv_write(data,'annual_cohort_examples.csv',rows);csv_write(data,'nearlinear_examples.csv',near);csv_write(data,'subset_bound_scenarios.csv',scenarios)
    calc['display_precision_audit']=q;calc['annual_cohort_examples']=rows;calc['nearlinear_examples']=near;calc['subset_comparison']={'nested_support_lower_bound':bound,'uniform_domain_mean_benchmark':benchmark,'upper_bound_without_extra_assumption':None,'scenarios':scenarios}
    validation['audit_extensions']={'seed':20260918,'randomized_cases':1100,'assertions':checks,'max_residuals':maxerr,'probability_scope':'Explicit display-error reference models, not posterior model selection.'}
    validation['assertions']+=checks;validation['randomized_cases_total']+=1100
    return calc,validation
