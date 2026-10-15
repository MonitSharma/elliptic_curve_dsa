"""Freeze and qualify only the predetermined four-stage wide circuit."""
from pathlib import Path
import hashlib,json,math,subprocess
root=Path(__file__).resolve().parent;up=root.parent/'product-exact-20261015'
tree=up/'wide-candidate-final';e=root/'evidence';e.mkdir(exist_ok=True)
assert (up/'wide-final.exit').read_text().strip()=='0'
assert '21 passed; 0 failed' in (up/'wide-final-native-tests.log').read_text()
freeze=json.loads((up/'WIDE_FREEZE.json').read_text())
assert hashlib.sha256((tree/'ops.bin').read_bytes()).hexdigest()==freeze['external_stream_sha256']
assert hashlib.sha256((up/'wide-candidate-final.patch').read_bytes()).hexdigest()==freeze['source_patch_sha256']
rows=[]
for name in ['parent','candidate']:
 p=up/f'wide-frozen-{name}-census.jsonl';data=p.read_bytes();(e/f'{name}-census.jsonl').write_bytes(data)
 r=[json.loads(x) for x in data.splitlines()];assert len(r)==4096
 assert sorted(x['batch'] for x in r)==list(range(4096)) and all(x['shots']==64 for x in r)
 rows.append({x['batch']:x for x in r})
a,b=rows;diff=[(a[i]['toffoli']-b[i]['toffoli'])/64 for i in range(4096)]
mean=sum(diff)/4096;se=math.sqrt(sum((x-mean)**2 for x in diff)/(4095*4096))
fail=[sum(bool(r['failures']) for r in x.values()) for x in rows]
assert fail[1]<=fail[0] and 141*fail[1]/4096<=18
assert all(x['dirty_shots']==0 for x in b.values()) and mean>15
summary={'status':'frozen_circuit_nonce_eligible_not_scored','label':'wide-frozen-four-stage-20261015','shots_each':262144,'batches_each':4096,'failed_batches':dict(zip(['parent','candidate'],fail)),'expected_failed_batches_per_packet':141*fail[1]/4096,'paired_mean_T_saving':mean,'saving_standard_error':se,'peak_Q':1464,'passes_failure_gate':True,'nonce_policy':'ascending_from_1_lowest_pass','submission_mode':'queue'}
(e/'qualification.json').write_text(json.dumps(summary,indent=2)+'\n')
(e/'FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\n')
(e/'frozen-candidate.patch').write_bytes((up/'wide-candidate-final.patch').read_bytes())
(e/'native-tests.log').write_bytes((up/'wide-final-native-tests.log').read_bytes())
tracked=subprocess.check_output(['git','-C',str(tree),'ls-files','-z']).decode().split('\0')
protected={p:hashlib.sha256((tree/p).read_bytes()).hexdigest() for p in tracked if p and not p.startswith('src/point_add/')}
for p,h in protected.items():
 original=subprocess.check_output(['git','-C',str(tree),'show','HEAD:'+p])
 assert hashlib.sha256(original).hexdigest()==h,p
(e/'protected.json').write_text(json.dumps(protected,indent=2)+'\n')
sources={str(p.relative_to(tree)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (tree/'src/point_add').rglob('*') if p.is_file()}
(e/'frozen-source.json').write_text(json.dumps(sources,indent=2)+'\n')
print(json.dumps(summary,indent=2))
