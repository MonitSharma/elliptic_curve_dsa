"""Append exact per-lane comparisons to the already frozen all-row analysis."""
import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'repair67-native-20261016';assert (d/'census-launcher.exit').read_text().strip()=='0';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for role in ['parent','candidate']:
    data=[json.loads(x) for x in (d/f'{role}-census.jsonl').read_text().splitlines()];assert len(data)==32768 and {x['batch'] for x in data}==set(range(32768));rows.append(data)
entries=[{(row['batch'],f['lane']):f for row in data for f in row['failures']} for data in rows]
for key in set(entries[0])&set(entries[1]):assert (entries[0][key]['k1'],entries[0][key]['k2'])==(entries[1][key]['k1'],entries[1][key]['k2'])
answer={'status':'COMPLETE_FIXED_SAMPLE_EXACT_FAILURE_LANE_COMPARISON','label':'repair-plus67-frozen-20261016','parent_rows_sha256':sha(d/'parent-census.jsonl'),'candidate_rows_sha256':sha(d/'candidate-census.jsonl'),'batches_each':32768,'shots_each':2097152,'categories':{}}
for category in ['all','value','phase','dirty']:
    sets=[{key for key,value in data.items() if category=='all' or value[category]} for data in entries];a,b=sets
    if category!='all':
        field=category+'_shots'
        for data,selected in zip(rows,sets):assert len(selected)==sum(x[field] for x in data)
    answer['categories'][category]={'parent_failed_shots':len(a),'candidate_failed_shots':len(b),'parent_only_failed_shots':len(a-b),'candidate_only_failed_shots':len(b-a),'same_failure_lanes':len(a&b)}
answer['scope']='All declared rows and lanes, not selected witnesses. Scalar equality checked on every commonly failing lane. Fresh source replays have different sequential MR coupling, so phase/overall lane changes are descriptive. No source changes, extra sampling or nonce work.'
target=d/'PER_SHOT_FAILURE_COMPARISON.json';assert not target.exists();target.write_text(json.dumps(answer,indent=2)+'\n');print(json.dumps(answer,indent=2),flush=True)
