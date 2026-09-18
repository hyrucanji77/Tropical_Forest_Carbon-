#!/usr/bin/env python3
"""Reproduce V7.1 source-support and accounting checks (standard library only).

Inputs are reported values or explicitly illustrative scenarios. No new plot
measurements, capture-route assignments, or updated global map are generated.
"""
from __future__ import annotations
import csv,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def dump(name,obj):
 (ROOT/'data'/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
def csvwrite(name,fields,rows):
 with (ROOT/'data'/name).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 src=json.loads((ROOT/'data/review_update_sources.json').read_text(encoding='utf-8'))
 tests=0
 def check(ok):
  nonlocal tests
  tests+=1
  if not ok:raise AssertionError(f'V7.1 check {tests} failed')
 def close(a,b):check(math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-10))
 q=src['initial_preprint'];lo,hi=q['response_carbon_range_MgC_ha']
 ratio=q['class5_carbon_PgC']*1e9/q['class5_area_ha']
 vals=[('class5_lower_edge',478.0),('class5_printed_mean',531.05),('class5_stock_area_ratio',ratio),('reported_map_maximum',605.0)]
 support=[{'quantity':k,'MgC_ha':v,'within_reported_marginal_response_range':lo<=v<=hi,'above_response_max_MgC_ha':max(0,v-hi)} for k,v in vals]
 close(ratio,536.3257329758882)
 check(support[0]['within_reported_marginal_response_range'])
 for z in support[1:]:check(not z['within_reported_marginal_response_range'])
 close(support[1]['above_response_max_MgC_ha'],8.05)
 close(support[2]['above_response_max_MgC_ha'],ratio-523)
 close(support[3]['above_response_max_MgC_ha'],82)
 check(q['regional_mean_MgC_ha']<478<hi)
 check(q['independent_class5_residual'] is None)
 p=src['gross_pair'];F=p['deforestation_GtC_yr'];U=p['forest_regrowth_GtC_yr'];delta=.1;r=1.5
 net=F-U;gross=F+U;eta=abs(net)/gross;shift=delta*gross/2
 close(net,.6);close(gross,3.2);close(eta,.1875);close(shift,.16)
 close((r+delta/2)*F-(r-delta/2)*U-r*net,shift)
 close(p['all_land_use_net_GtC_yr']-net,.8)
 # Alternative I changes an existing residual, not a universal allowance.
 base=-1.7
 close(base+1.,-.7);check(abs(base+1.)<abs(base))
 check(abs(0.+1.)>abs(0.))
 # A one-standard-deviation statement is not a hard support limit.
 check(src['budget_constraints'][0]['uncertainty_type']=='one_standard_deviation')
 # The ordering of census conditions needs rG >= 1 and S > 0.
 for G,L,rG,rL in [(120.,100.,1.1,1.15),(120.,100.,1.,1.01),(150.,100.,1.5,1.8)]:
  S=G-L;Sstar=rG*G-rL*L
  check(Sstar<S)
  check(rL>rG)
  close(Sstar-S,(rG-1)*G-(rL-1)*L)
 # Counterexample outside rG >= 1: lower net sink does not imply larger loss factor.
 G,L,rG,rL=120.,100.,.5,.45
 check(rG*G-rL*L<G-L);check(rL<rG)
 # The quoted voxel means do not show improvement towards integration.
 vox=q['volume_means_cm3'];check(abs(vox['voxel_1mm']-vox['integration'])>abs(vox['voxel_1cm']-vox['integration']))
 close((vox['displacement']-vox['voxel_1mm'])/vox['displacement']*100,4.03870967741936)
 # Biomass-volume requirements remain conditional conversions.
 close(478/(.47*.60),1695.035460992908)
 close(ratio/(.47*.60),1901.8643013329365)
 # Population size, segmentation success and allometric contrast are distinct quantities.
 tls=src['tls2trees'];close(tls['paired_reference_trees']/tls['manual_reference_trees']*100,82.20140515222482)
 close(src['calders2022']['AGB_TLS_Mg_ha']/src['calders2022']['AGB_allometry_Mg_ha'],409.9/231.9)
 summary={'edition':'7.1','status':'Analytical and source-transcription update; no new empirical map',
  'preprint_calibration_support':support,
  'support_warning':'Marginal response ranges do not prove joint predictor/architecture support or independent validation.',
  'gross_pair':{'period':'2015–2024','source_GtC_yr':F,'removal_GtC_yr':U,'net_GtC_yr':net,'sum_GtC_yr':gross,'eta':eta,
   'illustrative_delta':delta,'differential_net_shift_GtC_yr':shift,'remaining_net_GtC_yr':p['all_land_use_net_GtC_yr']-net,
   'remaining_net_status':'Rounded residual relative to reported total; not a separately measured component.'},
  'voxel_convergence_status':'Two reported grid means are insufficient to identify a consistent convergence sequence.',
  'capture_route_records_recovered':0,'new_global_calibration_total':None}
 dump('review_update_summary.json',summary)
 csvwrite('calibration_support.csv',list(support[0]),support)
 rows=[{'quantity':k,'GtC_yr':v,'status':'Selected source-reported pair; derived arithmetic' if k!='differential_shift' else 'Illustrative delta=0.1, not observed correction'} for k,v in [('deforestation',F),('regrowth',U),('net',net),('gross_sum',gross),('differential_shift',shift)]]
 csvwrite('gcb_gross_pair.csv',list(rows[0]),rows)
 rows=src['budget_constraints'];csvwrite('gcb_constraints.csv',list(rows[0]),rows)
 dump('review_update_validation.json',{'status':'PASS','assertions':tests,'mode':'deterministic','seed':None,
  'scope':'Source transcription and analytic constraints; not empirical forest validation','relative_tolerance':1e-12,'absolute_tolerance':1e-10})
 print(f'V7.1 checks: {tests} PASS')
if __name__=='__main__':main()
