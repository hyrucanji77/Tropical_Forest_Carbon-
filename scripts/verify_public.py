#!/usr/bin/env python3
"""Verify publication bytes and regenerate numerical evidence in a temporary directory.

Python 3.9+, standard library. Document-source fragments generated during numerical
reproduction stay in the temporary directory; no document source is distributed.
"""
from pathlib import Path, PurePosixPath
import hashlib,json,shutil,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
ALLOWED={'.pdf','.json','.csv','.py','.md','.cff'}
EXTRAS={'.gitignore','.github/workflows/verify.yml'}
def main():
 if not __debug__:raise RuntimeError('Run without Python -O.')
 manifest=json.loads((ROOT/'PUBLICATION_MANIFEST.json').read_text(encoding='utf-8'))
 expected=set(manifest['files'])|{'PUBLICATION_MANIFEST.json','PUBLICATION_VERIFICATION.json'}
 found=set()
 for p in ROOT.rglob('*'):
  rel=p.relative_to(ROOT).as_posix()
  if any(v in p.relative_to(ROOT).parts for v in ('.git','__pycache__')):continue
  if p.is_symlink():raise RuntimeError('Symlink: '+rel)
  if not p.is_file():continue
  if rel in EXTRAS:continue
  if p.suffix.lower() not in ALLOWED:raise RuntimeError('Prohibited publication format: '+rel)
  found.add(rel)
 if found!=expected:raise RuntimeError('Unexpected or missing files: '+str(sorted(found^expected)))
 for name,rec in manifest['files'].items():
  rel=PurePosixPath(name)
  if rel.is_absolute() or '..' in rel.parts:raise RuntimeError('Unsafe manifest path')
  p=ROOT/name
  if p.stat().st_size!=rec['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=rec['sha256']:raise RuntimeError('Integrity mismatch: '+name)
 outputs=json.loads((ROOT/'NUMERICAL_OUTPUTS.json').read_text())
 with tempfile.TemporaryDirectory(prefix='forest-carbon-v75-') as td:
  t=Path(td);shutil.copytree(ROOT/'scripts',t/'scripts',ignore=shutil.ignore_patterns('__pycache__'));shutil.copytree(ROOT/'data',t/'data')
  run=subprocess.run([sys.executable,'scripts/reproduce.py'],cwd=t,capture_output=True,text=True)
  if run.returncode:raise RuntimeError(run.stdout+'\n'+run.stderr)
  changed=[n for n in outputs if (t/'data'/n).read_bytes()!=(ROOT/'data'/n).read_bytes()]
  checknames=['validation.json','population_atmosphere_validation.json','stand_closure_validation.json','class5_comparison_validation.json','admissibility_validation.json','calibration_bias_validation.json','review_update_validation.json','support_budget_validation.json','structural_constraints_validation.json','sector_ranking_validation.json']
  checks={n:json.loads((t/'data'/n).read_text()) for n in checknames}
  if any(x.get('status')!='PASS' for x in checks.values()):raise RuntimeError('Numerical suite failure')
 report={'status':'FAIL' if changed else 'PASS','edition':'7.5','layout_revision':'figure2-alignment','build_revision':'overleaf-ready','files_checked':len(manifest['files']),'regenerated_public_outputs':len(outputs),'byte_identical':not changed,'nonidentical_files':changed,'checks':checks,'scope':'Integrity and analytical reproduction; not independent field validation.'}
 print(json.dumps(report,indent=2));return int(bool(changed))
if __name__=='__main__':
 try:sys.exit(main())
 except Exception as e:print(json.dumps({'status':'FAIL','error':str(e)},indent=2));sys.exit(1)
