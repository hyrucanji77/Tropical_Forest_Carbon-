#!/usr/bin/env python3
"""Apply the checked 5.0 -> 5.1 editorial patch; retain numerical research inputs.

Idempotent for this release. Unexpected source text raises an error rather than
silently patching another manuscript version. Recompile and remake the manifest
and archive after applying this script.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
REPO = 'https://github.com/hyrucanji77/Tropical_Forest_Carbon-'
RELEASE = REPO + '/releases/tag/v5.1'


def replace(path: str, before: str, after: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding='utf-8')
    if after in text and before not in text:
        return
    if text.count(before) != 1:
        raise RuntimeError(f'{path}: expected one exact source match, found {text.count(before)}')
    target.write_text(text.replace(before, after, 1), encoding='utf-8')


def main() -> None:
    replace('main.tex',
        r'No empirical correction to EDGAR is inferred. Because tropical fire \COtwo{} is included in its Deforestation category, however, a biological recalibration of that category requires compartment-resolved release timing, not solely revised pre-clearing stocks.',
        r'These synthetic transfers describe a physical release history. Applying them to EDGAR requires identifying whether the target is conversion-year stock-loss booking or atmospheric release: the inclusion of tropical fire \COtwo{} in Deforestation does not itself make a decay kernel part of the inventory operator. Section~\ref{sec:annual} distinguishes those accounting conventions.')
    replace('main.tex',
        r"The author declares no competing interests. Henry Arellano-Pe\~na owns the methodologies examined and is founder and director of NEBIOT S.A.S., the sole company currently affiliated with this work. For transparency, NEB001 supplies the CCA--Fuzzy Land Cover vegetation mapping and NEB002 the voxel, elemental-carbon and neural-network quantification chain underlying the historical estimate audited here \citep{Arellano2016,NEBIOTMethods}. These ownership and methodological relationships are stated explicitly alongside the author's declaration.",
        r'Henry Arellano-Pe\~na owns the methodologies examined and is founder and director of NEBIOT S.A.S., the sole company currently affiliated with this work. NEB001 supplies the CCA--Fuzzy Land Cover vegetation mapping and NEB002 the voxel, elemental-carbon and neural-network quantification chain underlying the historical estimate audited here \citep{Arellano2016,NEBIOTMethods}. These ownership and professional relationships are disclosed; the author declares no other competing interests.')
    replace('main.tex',
        r'The associated research snapshot is identified by release metadata and a SHA-256 manifest; the repository commit history records subsequent changes.',
        r'The versioned deposit is \href{' + RELEASE + r'}{research release 5.1}, which includes the compiled manuscript and the complete Overleaf archive. Its metadata and SHA-256 manifest identify the distributed files; the associated Git commit records the source snapshot. No archival DOI has been assigned.')
    replace('response_to_review.tex',
        'together with my statement of no competing interests.',
        'together with my declaration of no other competing interests beyond these disclosed relationships.')
    replace('README.md', 'Research snapshot **5.0**', 'Research snapshot **5.1**')
    replace('README.md',
        'The complete Overleaf ZIP is in `release/` after the build finishes.',
        'The complete Overleaf ZIP is `release/Tropical_Forest_Carbon_Overleaf_v5_1.zip`. Versioned files are published at ' + RELEASE + ' .')
    replace('README.md',
        "The paper records the author's no-competing-interests declaration and the specific NEB001/NEB002 methodological connection.",
        "The paper explicitly discloses these ownership/professional relationships, records the author's declaration of no other competing interests, and states the specific NEB001/NEB002 methodological connection.")
    replace('CITATION.cff', 'version: "5.0"', 'version: "5.1"')
    replace('CITATION.cff', '\nurl: "' + REPO + '"\n', '\nurl: "' + RELEASE + '"\n')
    replace('references.bib',
        'year = {2026}, howpublished = {GitHub research repository, snapshot 5.0},\n url = {' + REPO + '},',
        'year = {2026}, howpublished = {GitHub research repository, snapshot 5.1},\n url = {' + RELEASE + '},')
    replace('data/source_provenance.csv', 'Research snapshot5.0', 'Research snapshot5.1')
    replace('data/inputs.json', '"version": "5.0"', '"version": "5.1"')
    replace('scripts/make_manifest.py', "'release':'5.0'", "'release':'5.1'")
    replace('scripts/package_release.py', 'Tropical_Forest_Carbon_Overleaf_v5.zip', 'Tropical_Forest_Carbon_Overleaf_v5_1.zip')
    replace('scripts/package_release.py', "'version':'5.0'", "'version':'5.1'")
    changes = ROOT / 'CHANGES.md'
    text = changes.read_text(encoding='utf-8')
    heading = '# Research snapshot 5.1\n\n'
    if not text.startswith(heading):
        changes.write_text(heading + 'Clarifies conversion-year inventory booking versus physical release in the single-cohort example; consolidates the ownership and NEBIOT declaration; and pins the citation and availability statement to the versioned research release. Numerical inputs, identities and figure artwork are unchanged from 5.0.\n\n' + text, encoding='utf-8')
    record = {
        'release': '5.1',
        'base_release': REPO + '/releases/tag/v5.0',
        'base_research_commit': 'f8c617ef452e3e375833b51ed98174c0918ffe45',
        'changes': ['Clarify physical release versus inventory booking',
                    'Disclose methodology ownership and NEBIOT relationship with no other competing interests',
                    'Cite versioned deposit and update package metadata'],
        'numerical_research_inputs_changed': False,
        'figures_changed': False,
        'doi_assigned': False
    }
    (ROOT / 'audit/final_revision.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print('Applied research snapshot 5.1 patch.')


if __name__ == '__main__':
    main()
