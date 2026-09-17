#!/usr/bin/env python3
"""Finalize the concise availability section and metadata for research release 5.2."""
import json
from pathlib import Path
import finalize_snapshot

ROOT = Path(__file__).resolve().parents[1]
REPO = 'https://github.com/hyrucanji77/Tropical_Forest_Carbon-'


def main() -> None:
    version = json.loads((ROOT / 'data/inputs.json').read_text())['version']
    if version == '5.2':
        print('Research release 5.2 is already finalized.')
        return
    if version not in {'5.0', '5.1'}:
        raise RuntimeError('Unsupported source version: ' + version)
    finalize_snapshot.main()
    edits = {
        'main.tex': [('releases/tag/v5.1', 'releases/tag/v5.2'), ('research release 5.1', 'research release 5.2')],
        'README.md': [('**5.1**', '**5.2**'), ('releases/tag/v5.1', 'releases/tag/v5.2'), ('Overleaf_v5_1.zip', 'Overleaf_v5_2.zip')],
        'CITATION.cff': [('version: "5.1"', 'version: "5.2"'), ('releases/tag/v5.1', 'releases/tag/v5.2')],
        'references.bib': [('snapshot 5.1', 'snapshot 5.2'), ('releases/tag/v5.1', 'releases/tag/v5.2')],
        'data/source_provenance.csv': [('Research snapshot5.1', 'Research snapshot5.2')],
        'data/inputs.json': [('"version": "5.1"', '"version": "5.2"')],
        'scripts/make_manifest.py': [("'release':'5.1'", "'release':'5.2'")],
        'scripts/package_release.py': [("'version':'5.1'", "'version':'5.2'"), ('Overleaf_v5_1.zip', 'Overleaf_v5_2.zip')]
    }
    for path, pairs in edits.items():
        for old, new in pairs:
            finalize_snapshot.replace(path, old, new)
    p = ROOT / 'CHANGES.md'
    p.write_text('# Research snapshot 5.2\n\nConcise, directly linked availability statement and final pagination. Scientific equations, numerical inputs and artwork are unchanged from 5.1. Prior releases remain separately available.\n\n' + p.read_text(), encoding='utf-8')
    p = ROOT / 'audit/final_revision.json'
    record = json.loads(p.read_text())
    record['release'] = '5.2'
    record['prior_editorial_release'] = REPO + '/releases/tag/v5.1'
    record['changes'].append('Consolidate availability wording and avoid an unnecessary page break')
    p.write_text(json.dumps(record, indent=2) + '\n')
    print('Finalized research release 5.2.')


if __name__ == '__main__':
    main()
