"""Describe all terminal paired rows; never choose a source or sample subset."""
import json,math
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'repair53-native-20261016';assert (d/'census-launcher.exit').read_text().strip()=='0'
summary=json.loads((d/'census-summary.json').read_text());rows=[]
for role in ['parent','candidate']:
    data=[json.loads(x) for x in (d/f'{role}-census.jsonl').read_text().splitlines()];assert len(data)==32768
    rows.append({x['batch']:x for x in data})
a,b=rows;n=32768;assert set(a)==set(b)==set(range(n));answer={'status':'COMPLETE_FIXED_SAMPLE_DESCRIPTIVE_ANALYSIS','label':summary['label'],'parent_sha256':summary['parent_sha256'],'candidate_sha256':summary['candidate_sha256'],'all_rows_included':True,'categories':{}}
for category,field in [('all',None),('value','value_shots'),('phase','phase_shots'),('dirty','dirty_shots')]:
    av=[bool(a[i]['failures']) if field is None else a[i][field]>0 for i in range(n)];bv=[bool(b[i]['failures']) if field is None else b[i][field]>0 for i in range(n)]
    delta=[int(x)-int(y) for x,y in zip(av,bv)];mean=sum(delta)/n
    row={'parent_failed_batches':sum(av),'candidate_failed_batches':sum(bv),'parent_only_failed_batches':sum(x and not y for x,y in zip(av,bv)),'candidate_only_failed_batches':sum(y and not x for x,y in zip(av,bv)),'paired_failed_batches_per_packet_reduction':141*mean,'paired_reduction_standard_error':141*math.sqrt(sum((x-mean)**2 for x in delta)/(n*(n-1)))}
    if field:row.update(parent_failed_shots=sum(x[field] for x in a.values()),candidate_failed_shots=sum(x[field] for x in b.values()))
    answer['categories'][category]=row
answer['interpretation']='Descriptive finite fixed sample. Exact caches preserve the repair-parent function under an original-MR projection, but these source replays use their own sequential MR coupling. Category and phase differences do not by themselves identify a corrected failure source or establish a universal failure-rate reduction. No resampling, sample extension, endpoint selection or nonce work follows this analysis.'
(d/'failure-analysis.json').write_text(json.dumps(answer,indent=2)+'\n');print(json.dumps(answer,indent=2),flush=True)
