#!/usr/bin/env python3
"""Reproduce physical-volume shortfalls; no new field data or fit.
The absolute difference is labelled shortfall because every reconstruction is below the reference."""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import json, csv
ROOT=Path(__file__).resolve().parents[1]

def main():
    source=json.loads((ROOT/'data/original_measurement_evidence.json').read_text())
    ref=Decimal(source['volume_validation']['reference_mean_cm3'])
    rows=[]; tex=[]
    for item in source['volume_validation']['methods']:
        mean=Decimal(item['mean_cm3'])
        difference=Decimal(100)*abs(mean-ref)/ref
        shown=difference.quantize(Decimal('.1'),rounding=ROUND_HALF_UP)
        rows.append({'method':item['method'],'mean_volume_cm3':str(mean),
                     'mean_volume_difference_percent':str(difference),
                     'displayed_difference_percent':str(shown)})
        tex.append(f"{item['latex_label']} & {mean:,.2f} & {shown} "+r'\\')
    assert [r['displayed_difference_percent'] for r in rows]==['0.0','1.8','2.3','4.0']
    with (ROOT/'data/physical_validation_summary.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    (ROOT/'data/physical_validation_rows.tex').write_text('\n'.join(tex)+'\n')
    print('Physical-validation table reproduced from published mean volumes.')
if __name__=='__main__':main()
