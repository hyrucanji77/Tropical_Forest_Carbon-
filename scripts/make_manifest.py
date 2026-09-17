#!/usr/bin/env python3
"""Generate a manifest for the public research snapshot, excluding build debris."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ROOT_FILES={'main.tex','main.pdf','main.bbl','references.bib','figure_plates.tex',
 'response_to_review.tex','response_to_review.pdf','response_to_review.bbl',
 'README.md','SOURCE_AVAILABILITY.md','RIGHTS.md','CITATION.cff','CHANGES.md'}
DIRS={'scripts','data','figures','source_figures','audit'}
def members():
 for p in sorted(ROOT.rglob('*')):
  if not p.is_file():continue
  rel=p.relative_to(ROOT)
  if '__pycache__' in rel.parts or p.suffix in {'.pyc','.aux','.log','.out','.blg','.fls','.fdb_latexmk'}:continue
  if (len(rel.parts)==1 and p.name in ROOT_FILES) or rel.parts[0] in DIRS:yield p
if __name__=='__main__':
 obj={'release':'5.2','snapshot_date':'2026-09-16','repository':'https://github.com/hyrucanji77/Tropical_Forest_Carbon-',
 'algorithm':'SHA-256','scope':'Distributed research files; excludes this manifest, verification result and ZIP to avoid recursion.', 'files':{}}
 for p in members():obj['files'][p.relative_to(ROOT).as_posix()]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 (ROOT/'manifest.json').write_text(json.dumps(obj,indent=2)+'\n');print('Manifest:',len(obj['files']),'files')
