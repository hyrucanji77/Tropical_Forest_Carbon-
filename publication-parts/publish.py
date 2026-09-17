#!/usr/bin/env python3
"""Publish the explicitly supplied, hash-verified research source archive."""
import base64, hashlib, io, json, lzma, os, pathlib, subprocess, tarfile
root=pathlib.Path.cwd()
ready=json.loads((root/'publication-parts/READY.json').read_text())
encoded=''.join((root/'publication-parts'/p).read_text().strip() for p in ready['parts'])
packed=base64.b64decode(encoded,validate=True)
if hashlib.sha256(packed).hexdigest()!=ready['sha256']:
    raise SystemExit('Compressed source SHA-256 mismatch')
raw=lzma.decompress(packed)
allowed_dirs={'scripts','data','source_figures'}
allowed_files={'main.tex','references.bib','figure_plates.tex','response_to_review.tex','README.md','RIGHTS.md','SOURCE_AVAILABILITY.md','CHANGES.md','CITATION.cff'}
paths=[]
with tarfile.open(fileobj=io.BytesIO(raw),mode='r:') as archive:
    for member in archive:
        path=pathlib.PurePosixPath(member.name)
        if not member.isfile() or path.is_absolute() or '..' in path.parts:
            raise SystemExit('Unsafe archive member')
        if not ((len(path.parts)==1 and str(path) in allowed_files) or path.parts[0] in allowed_dirs):
            raise SystemExit('Unexpected archive path: '+str(path))
        target=root.joinpath(*path.parts)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(archive.extractfile(member).read())
        paths.append(str(path))
(root/'figures').mkdir(exist_ok=True)
(root/'audit').mkdir(exist_ok=True)
subprocess.run(['python3','scripts/reproduce.py'],check=True)
receipt={'snapshot':'5.0','source_archive_sha256':ready['sha256'],'source_files':paths,'source_transport_commit':os.environ.get('GITHUB_SHA'),'scope':'Source and numerical publication; PDF build is a separate workflow.'}
(root/'audit/source_deposit.json').write_text(json.dumps(receipt,indent=2)+'\n')
subprocess.run(['git','config','user.name','github-actions[bot]'],check=True)
subprocess.run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'],check=True)
subprocess.run(['git','add','--']+paths+['data','audit/source_deposit.json'],check=True)
subprocess.run(['git','commit','-m','Deposit forest-carbon research source and reproducible numerical results (snapshot 5.0)'],check=True)
auth=base64.b64encode(('x-access-token:'+os.environ['GH_TOKEN']).encode()).decode()
subprocess.run(['git','-c','http.extraheader=AUTHORIZATION: basic '+auth,'push','origin','HEAD:main'],check=True)
print('Research source deposited; archive integrity and numerical execution passed.')
