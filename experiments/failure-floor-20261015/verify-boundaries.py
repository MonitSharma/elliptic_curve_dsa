from pathlib import Path
import json,re,collections,hashlib,tarfile
root=Path(__file__).resolve().parent;ev=root/'evidence';log=ev/'generate.log';text=log.read_text();p=2**256-2**32-977
fields={'tick':'tick','window':'window','shift':'shift','low_L':'low_L','E':'E','Nm':'nm','m':'m','C':'C','c':'signed_boundary_c'}
reconstructed={x['shot']:x for x in json.loads((root/'boundary-reconstruction.json').read_text())['cases']}
folds=[dict(re.findall(r'(\w+)=([^ ]+)',l))for l in text.splitlines()if l.startswith('FOLD_BOUNDARY ')]
assert len(folds)==29
for row in folds:
 assert row['family']=='floor31';r=reconstructed[int(row['shot'])]
 assert all(int(row[k])==r[v] for k,v in fields.items()),row
 assert row['low_matches']=='true'
windows=[]
for line in text.splitlines():
 if not line.startswith('WINDOW_EVENT '):continue
 v=dict(re.findall(r'(\w+)=([^ ]+)',line));assert v['family']=='floor31'
 a,b,got,want,diff=[int(v[k],16)for k in ['a','b','got','want','diff']];shift=int(v['shift']);width=int(v['value_width'])+20;cin=int(v['cin']);sign=-1 if v['inv']=='true' else 1
 low=(a>>shift)%2**width;term=sign*(b+cin);carry=(low+term)//2**width;replaced=a-low*2**shift+((low+term)%2**width)*2**shift
 assert got==replaced%p
 assert want==(a+term*2**shift)%p
 assert diff==(-carry*2**(shift+width))%p
 windows.append({'shot':int(v['shot']),'at':int(v['at']),'shift':shift,'top':shift+width,'signed_carry':carry,'signed_delta':-carry*2**(shift+width),'source_cin':cin,'exact_modular_and_truncated_outputs_match':True})
assert len(windows)==3
stage={r['floor_shot']:r for r in json.loads((root/'square-first-stage.json').read_text())}
for shot in [20,26]:assert sum(w['signed_delta']for w in windows if w['shot']==shot)==stage[shot]['signed_delta_x']
summaries=[l for l in text.splitlines()if l.startswith('PAY_SUMMARY ')];assert len(summaries)==2 and 'first_events=0' in summaries[1] and 'final_bad=0' in summaries[1]
assert not any(l.startswith(('WINDOW_EVENT family=independent','STAGE_EVENT family=independent'))for l in text.splitlines())
assert (ev/'stream.sha256').read_text().split()[0]=='95e771bae57bd96e75c11b569faf2f87cd7dfa52b227b40dd16e40a301d8e122'
out={'qualified_score':None,'direct_fold_matches':29,'exact_square_window_events':windows,'square_stage_deltas_explained':2,'all_31_first_failures_localized':True,'controls':256,'control_events':0,'stream_equals_parent':True,'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()}
(root/'boundary-verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
