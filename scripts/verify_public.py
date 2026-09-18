#!/usr/bin/env python3
"""Verify publication-only files and run computations in a temporary directory."""
from pathlib import Path
import csv, hashlib, io, json, math, shutil, subprocess, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
def equal(a,b):
 if isinstance(a,bool) or isinstance(b,bool):return type(a)==type(b) and a==b
 if isinstance(a,(float,int)) and isinstance(b,(float,int)):return math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-10)
 if type(a)!=type(b):return False
 if isinstance(a,dict):return a.keys()==b.keys() and all(equal(a[k],b[k]) for k in a)
 if isinstance(a,list):return len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
 return a==b
def compatible(name,a,b):
 if a==b:return True
 if name.endswith('.json'):return equal(json.loads(a),json.loads(b))
 def parse(raw):
  out=[]
  for row in csv.reader(io.StringIO(raw.decode('utf-8'))):
   vals=[]
   for x in row:
    try:vals.append(float(x))
    except ValueError:vals.append(x)
   out.append(vals)
  return out
 return equal(parse(a),parse(b))
def main():
 if not __debug__:raise RuntimeError('Run without -O.')
 manifest=json.loads((ROOT/'PUBLICATION_MANIFEST.json').read_text())
 for name,rec in manifest['files'].items():
  p=(ROOT/name).resolve()
  if ROOT not in p.parents or p.is_symlink() or not p.is_file():raise RuntimeError('Invalid path: '+name)
  if p.stat().st_size!=rec['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=rec['sha256']:raise RuntimeError('Integrity failure: '+name)
 outputs=json.loads((ROOT/'NUMERICAL_OUTPUTS.json').read_text())
 changed=[];bad=[]
 with tempfile.TemporaryDirectory(prefix='forest-carbon-check-') as td:
  target=Path(td)
  shutil.copytree(ROOT/'scripts',target/'scripts',ignore=shutil.ignore_patterns('__pycache__'))
  shutil.copytree(ROOT/'data',target/'data')
  run=subprocess.run([sys.executable,'scripts/reproduce.py'],cwd=target,capture_output=True,text=True)
  if run.returncode:raise RuntimeError(run.stdout+'\n'+run.stderr)
  for name in outputs:
   a=(ROOT/'data'/name).read_bytes();b=(target/'data'/name).read_bytes()
   if a!=b:changed.append(name)
   if not compatible(name,a,b):bad.append(name)
  checks={name:json.loads((target/'data'/name).read_text()) for name in ['validation.json','population_atmosphere_validation.json','stand_closure_validation.json','class5_comparison_validation.json','admissibility_validation.json','calibration_bias_validation.json']}
 report={'status':'FAIL' if bad else 'PASS','edition':'7.0','files_checked':len(manifest['files']),'regenerated_public_outputs':len(outputs),'byte_identical':not changed,'nonidentical_files':changed,'incompatible_files':bad,'checks':checks,'scope':'Integrity and analytical reproduction; not empirical field validation.'}
 print(json.dumps(report,indent=2));return int(bool(bad))
if __name__=='__main__':
 try:sys.exit(main())
 except Exception as e:print(json.dumps({'status':'FAIL','error':str(e)},indent=2));sys.exit(1)
