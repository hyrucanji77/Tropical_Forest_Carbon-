#!/usr/bin/env python3
"""Create the Overleaf archive from the verified manifest-backed files."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
 obj=json.loads((ROOT/'manifest.json').read_text());paths=list(obj['files'])+['manifest.json']
 if (ROOT/'verification.json').is_file():paths+=['verification.json']
 dest=ROOT/'release';dest.mkdir(exist_ok=True);archive=dest/'Tropical_Forest_Carbon_Overleaf_v5.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for name in sorted(paths):
   raw=(ROOT/name).read_bytes()
   if name in obj['files'] and hashlib.sha256(raw).hexdigest()!=obj['files'][name]['sha256']:
    raise RuntimeError('Changed after manifest: '+name)
   z.writestr(name,raw)
 metadata={'version':'5.0','snapshot_date':'2026-09-16','archive':archive.name,'bytes':archive.stat().st_size,
 'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'repository':obj['repository'],'doi':None,
 'evidence_status':'Analytical research and published-data audit; not a new field inventory.'}
 (dest/'release.json').write_text(json.dumps(metadata,indent=2)+'\n');print(json.dumps(metadata,indent=2))
