#!/usr/bin/env python3
"""Finite-state checks of calibration-label inheritance and population transfer.

Uses synthetic distributions only. Conditional expectations are computed exactly
on the supplied finite support; no trained learner, LiDAR observations, forest
inventory or empirical bias magnitude is implied. Python standard library only.
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
SEED = 20260922

def vector(values: Sequence[float], name: str) -> list[float]:
    result = [float(v) for v in values]
    if not result or any(not math.isfinite(v) for v in result):
        raise ValueError(name + ' requires a nonempty finite vector')
    return result

def probabilities(values: Sequence[float]) -> list[float]:
    result = vector(values, 'probabilities')
    if any(v < 0 for v in result) or not math.isclose(math.fsum(result), 1., rel_tol=0., abs_tol=1e-12):
        raise ValueError('Nonnegative probabilities summing to one required')
    return result

def conditional_mean(prob: Sequence[float], values: Sequence[float], labels: Sequence[int]) -> dict[int, float]:
    p, v = probabilities(prob), vector(values, 'values')
    if len(p) != len(v) or len(p) != len(labels):
        raise ValueError('Finite-state arrays must have equal lengths')
    if any(not isinstance(k, int) or isinstance(k, bool) for k in labels):
        raise ValueError('Integer sensor-state labels required')
    means = {}
    for k in sorted(set(labels)):
        mass = math.fsum(pi for pi, ki in zip(p, labels) if ki == k)
        if mass > 0:
            means[k] = math.fsum(pi*vi for pi,vi,ki in zip(p,v,labels) if ki == k)/mass
    return means

def inherited_bias(prob: Sequence[float], carbon: Sequence[float], bias: Sequence[float], labels: Sequence[int]) -> dict:
    p = probabilities(prob)
    c, b = vector(carbon, 'carbon'), vector(bias, 'bias')
    if len({len(p), len(c), len(b), len(labels)}) != 1:
        raise ValueError('Finite-state arrays must have equal lengths')
    y = [ci+bi for ci,bi in zip(c,b)]
    mc, my, mb = conditional_mean(p,c,labels), conditional_mean(p,y,labels), conditional_mean(p,b,labels)
    return {'true_conditional_mean':mc, 'label_conditional_mean':my, 'conditional_reference_bias':mb,
            'difference':{k:my[k]-mc[k] for k in mc}}

def main() -> None:
    if not __debug__:
        raise RuntimeError('Run without -O; regression checks must remain active')
    count = 0
    residuals: dict[str,float] = {}
    def check(group: str, left: float, right: float) -> None:
        nonlocal count
        count += 1
        err=abs(left-right)
        residuals[group] = max(err,residuals.get(group,0.))
        if not math.isclose(left,right,rel_tol=1e-11,abs_tol=1e-9):
            raise AssertionError((group,left,right,err))
    rng=random.Random(SEED)
    for _ in range(1000):
        n=rng.randint(4,24)
        raw=[rng.uniform(.05,1) for i in range(n)]
        p=[v/math.fsum(raw) for v in raw]
        rawq=[rng.uniform(.05,1) for i in range(n)]
        q=[v/math.fsum(rawq) for v in rawq]
        c=[rng.uniform(1,500) for i in range(n)]
        b=[rng.uniform(-50,50) for i in range(n)]
        labels=[i%3 for i in range(n)]
        z=inherited_bias(p,c,b,labels)
        qc=conditional_mean(q,c,labels)
        for k in z['difference']:
            check('label_inheritance',z['difference'][k],z['conditional_reference_bias'][k])
            check('conditional_transfer',z['label_conditional_mean'][k]-qc[k],
                  z['conditional_reference_bias'][k]+z['true_conditional_mean'][k]-qc[k])
        # Same biological response, changed architectural population probabilities.
        check('population_shift', math.fsum(pi*ci for pi,ci in zip(p,c))-math.fsum(qi*ci for qi,ci in zip(q,c)),
              math.fsum(ci*(pi-qi) for ci,pi,qi in zip(c,p,q)))
        # Law of total variance for the oracle source conditional mean.
        mean=math.fsum(pi*ci for pi,ci in zip(p,c))
        within=math.fsum(pi*(ci-z['true_conditional_mean'][ki])**2 for pi,ci,ki in zip(p,c,labels))
        between=math.fsum(pi*(z['true_conditional_mean'][ki]-mean)**2 for pi,ki in zip(p,labels))
        total=math.fsum(pi*(ci-mean)**2 for pi,ci in zip(p,c))
        check('conditional_variance',within+between,total)
    p=[.5,.5];q=[.2,.8];mass=[100.,200.]
    source=math.fsum(a*b for a,b in zip(p,mass));target=math.fsum(a*b for a,b in zip(q,mass))
    check('architecture_example',source,150.)
    check('architecture_example',target,180.)
    check('architecture_example',source-target,-30.)
    check('architecture_example',(source-target)/target,-1/6)
    # Nonzero biases can cancel conditionally; universal inheritance is not assumed.
    cancel=inherited_bias([.5,.5],[100,200],[20,-20],[0,0])
    check('zero_conditional_bias',cancel['difference'][0],0.)
    for args in [([],[],[],[]),([1],[1,2],[0],[0]),([-.1,1.1],[1,2],[0,0],[0,1]),
                 ([.5,.4],[1,2],[0,0],[0,1]),([1],[math.nan],[0],[0]),([1],[1],[0],[True])]:
        count+=1
        try: inherited_bias(*args)
        except ValueError: pass
        else: raise AssertionError('Invalid finite-state input accepted')
    # Exact signed-noise enumeration verifies MSE=b0^2+sigma^2/n for n=1,2,3.
    from itertools import product
    bias=-30.;sigma=10.
    for n in (1,2,3):
        mse=math.fsum((bias+sigma*sum(signs)/n)**2 for signs in product((-1,1),repeat=n))/2**n
        check('shared_bias_mse',mse,bias**2+sigma**2/n)
    rows=[{'independent_labels':n,'shared_bias':bias,'individual_noise_sd':sigma,
           'mean_squared_error':bias**2+sigma**2/n,'root_mean_squared_error':math.sqrt(bias**2+sigma**2/n)}
          for n in (1,10,100,1000,10000)]
    DATA.mkdir(exist_ok=True)
    with (DATA/'calibration_bias_examples.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    summary={'evidence_status':'Synthetic finite-state analytical examples, not measured forest or LiDAR bias.',
             'architecture_population':{'carbon_states':mass,'calibration_probabilities':p,'application_probabilities':q,
                 'source_mean_prediction':source,'target_mean_carbon':target,'prediction_minus_target':source-target,
                 'relative_error':(source-target)/target},
             'shared_bias_example':rows,'zero_conditional_bias_example':cancel,
             'interpretation':'Spatial precision alone does not remove a nonzero conditional reference-label bias; '
                 'direct material reconstruction is a distinct calibration route. Zero conditional bias gives no inherited conditional error.'}
    validation={'status':'PASS','seed':SEED,'randomized_cases':1000,'assertions':count,
                'absolute_tolerance':1e-9,'relative_tolerance':1e-11,'max_absolute_residuals':residuals,
                'scope':'Conditional-expectation algebra on synthetic finite supports; no empirical fitting or validation.'}
    for name,obj in [('calibration_bias_summary.json',summary),('calibration_bias_validation.json',validation)]:
        (DATA/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps(validation,indent=2))

if __name__=='__main__': main()
