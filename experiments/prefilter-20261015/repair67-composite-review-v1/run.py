from pathlib import Path
import json,os,re,subprocess,statistics
root=Path(__file__).resolve().parent
ops=root.parent/'product-exact-20261015/repair-to67-rank-20261016/repair-67-retained-1024-proxy.bin'
model=root.parent/'prefilter-20261015/model-source'
def run(name,first,count,look,fast,shadow=False,full=False,force=False):
 env=os.environ.copy()
 for key in ['FAST_ZERO_DISPATCH','PACKED_ZERO_SHADOW','EARLY_FULLSTATE_SHADOW','FIXED_TRANSFER_SHADOW','FORCE_FULL_FALLBACK']:env.pop(key,None)
 env['CANDIDATE_SEED_SHADOW']='1'
 if fast:env['FAST_ZERO_DISPATCH']='1'
 if force:env['FORCE_FULL_FALLBACK']='1'
 if shadow:env['PACKED_ZERO_SHADOW']='1'
 if full:env['EARLY_FULLSTATE_SHADOW']='1';env['FIXED_TRANSFER_SHADOW']='1'
 with (root/(name+'.log')).open('w') as out,(root/(name+'.err')).open('w') as err:
  subprocess.run([str(root/'tool/target/release/value_prefilter'),str(ops),str(first),str(count),'2',str(root/(name+'.jsonl')),str(model),str(look)],env=env,stdout=out,stderr=err,check=True)
 rows=sorted(map(json.loads,(root/(name+'.jsonl')).read_text().splitlines()),key=lambda r:r['nonce'])
 assert len(rows)==count and [r['nonce'] for r in rows]==list(range(first,first+count))
 assert all(not r['authoritative_rejection'] and not r['proof_accepted'] for r in rows)
 error=(root/(name+'.err')).read_text()
 assert 'CANDIDATE_OWN_FIAT_PROTECTED_4096_BYTE_CONTROLS_PASS' in error
 if force:assert error.count('FORCED_SCHEDULER_PROTECTED_KIND_PASS')==count
 if full:assert 'EARLY_FULLSTATE_AND_PHYSICAL_RNG9024_PASS' in error and 'FIXED445_GUARD_CONDITIONAL_KNOWN_BITS_PASS' in error
 wall=float(re.search(r'wall_seconds=([0-9.]+)',(root/(name+'.log')).read_text())[1])
 return rows,wall
a,_=run('forced2-generic',1,2,1,False,force=True)
b,_=run('forced2-threaded',1,2,1,True,force=True)
assert a==b and all(not row['provisional_wrong_value'] for row in a)
for name,first,count,look in [('shadow128',1,128,128),('partial',17,11,9)]:
 ref,_=run(name+'-generic',first,count,look,False,True,name=='shadow128')
 actual,_=run(name+'-threaded',first,count,look,True,True)
 assert actual==ref
times={'baseline':[],'threaded':[]};reference=None
for trial in range(3):
 for mode in (['baseline','threaded'] if trial%2==0 else ['threaded','baseline']):
  rows,wall=run(f'{mode}-{trial}',1,4096,4096,mode=='threaded')
  if reference is None:reference=rows
  assert rows==reference
  times[mode].append(wall)
report={'status':'DISABLED_REPAIRED67_CONDITIONAL_PIPELINE_QUALIFICATION_PASS','candidate_sha256':'0beec42b117e5f623736c4171e156d8ffdfaeeb585285636f91bab2838e7c10b','times_seconds':times,'median_seconds':{k:statistics.median(v) for k,v in times.items()},'all4096_rows_identical':True,'protected_zeroMR_shadow128_and_partial':True,'protected_full9024_q_b_phase_physicalMR':True,'authoritative_rejection':False,'nonce_selected':None,'production_changed':False}
(root/'RESULT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
