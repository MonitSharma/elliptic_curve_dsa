"""Executed-cost control on fresh valid points; never a statistical verdict."""
import hashlib,json,statistics,subprocess
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;n=ws/'product-classical-twelve-native-20261019'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
assert (r/'run.exit').read_text().strip()=='0' and (n/'run.exit').read_text().strip()=='0'
assert not (r/'component').exists();out=r/'component';out.mkdir()
binary=ws/'simd-census-v2-20261016/bin/simd_census_v2';assert sha(binary)=='790e92266ea67ec54ef701b2deed76fe8d0b766b411ca9eab877f82ae2c11a66'
paths={'classical9':ws/'product-classical-nine-20261019/candidate/ops.bin','classical12':n/'candidate/ops.bin'}
assert sha(paths['classical9'])=='76271c7d66785b62ec4077ec241e80d3645841ba898cf8b633c377099da687c1'
assert sha(paths['classical12'])=='17c767f514ca98ad02d4da9e5b1dbedf67189e5c70b7b15916adc0f0c2f0a7f7'
label='classical12-component-executed-20261019-v1';batches=64
decl={'declared_at_utc':datetime.now(timezone.utc).isoformat(),'label':label,'batches':batches,'shots_per_batch':64,'workers':1,
 'scope':'Fresh valid-point executed-cost and paired state-failure equality control ONLY. This is not a failure-rate gate, gate verdict, nonce packet, benchmark or record. Source is already finished/frozen; do not tune it to these inputs.',
 'streams':{k:{'path':str(p),'sha256':sha(p)} for k,p in paths.items()},'statistical_gate_still_required':True,'no_nonce_search':True}
(out/'DECLARATION.json').write_text(json.dumps(decl,indent=2)+'\n')
rows={}
for key,path in paths.items():
    with (out/(key+'.log')).open('xb') as f:subprocess.run([str(binary),str(path),label,'0',str(batches),'1',str(out/(key+'.jsonl')),'0'],stdout=f,stderr=subprocess.STDOUT,check=True)
    rows[key]={x['batch']:x for x in map(json.loads,(out/(key+'.jsonl')).open())}
    assert sorted(rows[key])==list(range(batches)) and all(x['shots']==64 and x.get('skipped',0)==0 for x in rows[key].values())
a,b=rows['classical9'],rows['classical12'];deltas=[]
for i in a:
    assert {k:v for k,v in a[i].items() if k!='toffoli'}=={k:v for k,v in b[i].items() if k!='toffoli'},'All paired value/phase/dirty diagnostics must match'
    assert a[i]['toffoli']>=b[i]['toffoli'];deltas.append((a[i]['toffoli']-b[i]['toffoli'])/64)
assert all(sha(path)==decl['streams'][key]['sha256'] for key,path in paths.items())
result={'status':'FRESH_VALID_POINT_COMPONENT_SAVING_VERIFIED','label':label,'batches':batches,'shots_each':64*batches,'additional_mean_executed_Toffolis_saved':statistics.mean(deltas),'saving_standard_error':statistics.stdev(deltas)/batches**.5,
 'every_paired_value_phase_and_dirty_diagnostic_identical':True,'stream_sha256':{k:sha(p) for k,p in paths.items()},'rows_sha256':{k:sha(out/(k+'.jsonl')) for k in paths},
 'scope':'Component-only count/equality diagnostic. No failure-rate gate verdict, official benchmark, nonce screen or full QxT resource record.'}
(r/'COMPONENT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
