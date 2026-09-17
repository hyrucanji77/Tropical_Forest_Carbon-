#!/usr/bin/env python3
"""Check manifest integrity and reproduce the numerical research outputs.

An unsigned manifest detects accidental changes, not authenticity. JSON and CSV
numbers may differ across supported Python platforms within 1e-10 absolute and
1e-12 relative tolerance; labels, exact decimal strings and LaTeX remain exact.
"""
from __future__ import annotations
import csv, hashlib, io, json, math, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
GENERATED=(
 'calculations.json','historical_calculations.csv','density_audit.csv','paired_source_sink.csv',
 'validation.json','density_rows.tex','historical_rows.tex','paired_rows.tex','derived.tex',
 'support_comparison.csv','interval_swap_diagnostic.csv','regrowth_examples.csv','census_differential.csv',
 'census_rows.tex','normalization_diagnostic.csv','carbon_fraction_sensitivity.csv','census_criteria.csv',
 'power_thresholds.csv','timing_examples.csv','edgar_land_reference.csv','display_precision_audit.json',
 'display_model_normalization.csv','printed_percentage_audit.csv','annual_cohort_examples.csv',
 'nearlinear_examples.csv','subset_bound_scenarios.csv')
REQUIRED=('main.tex','main.pdf','main.bbl','references.bib','README.md','response_to_review.tex',
 'response_to_review.pdf','scripts/reproduce.py','scripts/extensions.py','scripts/audit_extensions.py',
 'scripts/verify_package.py','data/inputs.json','data/source_provenance.csv','figures/figure_plates.pdf',
 'SOURCE_AVAILABILITY.md','RIGHTS.md','CITATION.cff')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def equal(a,b):
 if isinstance(a,bool) or isinstance(b,bool):return type(a)==type(b) and a==b
 if isinstance(a,(float,int)) and isinstance(b,(float,int)):
  return math.isclose(a,b,abs_tol=1e-10,rel_tol=1e-12)
 if type(a)!=type(b):return False
 if isinstance(a,dict):return a.keys()==b.keys() and all(equal(a[k],b[k]) for k in a)
 if isinstance(a,list):return len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
 return a==b

def compatible(name,a,b):
 if a==b:return True
 if name.endswith('.json'):return equal(json.loads(a),json.loads(b))
 if name.endswith('.csv'):
  def rows(raw):
   out=[]
   for row in csv.reader(io.StringIO(raw.decode('utf-8'))):
    vals=[]
    for item in row:
     try: vals.append(float(item))
     except ValueError: vals.append(item)
    out.append(vals)
   return out
  return equal(rows(a),rows(b))
 return False

def main():
 if not __debug__:raise RuntimeError('Run without -O.')
 manifest=json.loads((ROOT/'manifest.json').read_text());errors=[]
 for name in REQUIRED:
  if not (ROOT/name).is_file():errors.append(name+': required file absent')
 for name,record in manifest['files'].items():
  p=(ROOT/name).resolve()
  if ROOT not in p.parents:errors.append(name+': invalid manifest path');continue
  if not p.is_file() or p.stat().st_size!=record['bytes'] or sha(p)!=record['sha256']:
   errors.append(name+': integrity mismatch')
 if errors:raise RuntimeError('; '.join(errors))
 before={name:(ROOT/'data'/name).read_bytes() for name in GENERATED}
 run=subprocess.run([sys.executable,str(ROOT/'scripts/reproduce.py')],cwd=ROOT,capture_output=True,text=True)
 if run.returncode:raise RuntimeError(run.stdout+'\n'+run.stderr)
 changed=[];bad=[]
 for name,old in before.items():
  new=(ROOT/'data'/name).read_bytes()
  if old!=new:changed.append(name)
  if not compatible(name,old,new):bad.append(name)
  # Keep the manifest-backed distributed snapshot unchanged after verification.
  (ROOT/'data'/name).write_bytes(old)
 result={'status':'FAIL' if bad else 'PASS','release':manifest['release'],
 'manifest_members_checked':len(manifest['files']),'numerical_files_regenerated':len(GENERATED),
 'byte_identical':not changed,'nonidentical_files':changed,'incompatible_files':bad,
 'numeric_absolute_tolerance':1e-10,'numeric_relative_tolerance':1e-12,
 'analytical_checks':json.loads((ROOT/'data/validation.json').read_text()),
 'scope':'Integrity and computational reproduction, not empirical validation or digital authentication.'}
 print(json.dumps(result,indent=2));return int(bool(bad))
if __name__=='__main__':
 try:sys.exit(main())
 except (OSError,ValueError,KeyError,RuntimeError) as exc:
  print(json.dumps({'status':'FAIL','error':str(exc)},indent=2));sys.exit(1)
