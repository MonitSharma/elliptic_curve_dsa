from pathlib import Path
import json,os,re,subprocess,time,statistics,hashlib
r=Path(__file__).resolve().parent;old=r.parent/'repair67-conditional-filter-20261016'
ops=r.parent/'product-exact-20261015/repair-to67-rank-20261016/repair-67-retained-1024-proxy.bin'
model=r.parent/'prefilter-20261015/model-source'
assert hashlib.sha256((old/'evidence.tar.gz').read_bytes()).hexdigest()=='db095518788bfafb6cdf0ded3a1172a9e570a14988e48a502d13ab76d71d70f0'
manifest=json.loads((old/'manifest.json').read_text())
def prior(name):
 p=old/(name+'.jsonl');assert hashlib.sha256(p.read_bytes()).hexdigest()==manifest[name+'.jsonl']
 return sorted(map(json.loads,p.read_text().splitlines()),key=lambda x:x['nonce'])
reference=prior('baseline-0');assert len(reference)==4096
for name in ['baseline-1','baseline-2','threaded-0','threaded-1','threaded-2']:assert prior(name)==reference
reports=[]
def run(name,first,count,look,fused,shadow=False,full=False,force=False):
 env=os.environ.copy()
 for key in ['SCALAR_FAST_LIB','FAST_ZERO_DISPATCH','PACKED_ZERO_SHADOW','EARLY_FULLSTATE_SHADOW','FIXED_TRANSFER_SHADOW','FORCE_FULL_FALLBACK','FUSED_GUARD','FUSED_GUARD_SHADOW']:env.pop(key,None)
 env['CANDIDATE_SEED_SHADOW']='1'
 if fused:env['FUSED_GUARD']='1'
 if shadow:env['PACKED_ZERO_SHADOW']='1';env['FUSED_GUARD_SHADOW']='1'
 if full:env['EARLY_FULLSTATE_SHADOW']='1';env['FIXED_TRANSFER_SHADOW']='1'
 if force:env['FORCE_FULL_FALLBACK']='1'
 started=time.monotonic()
 with (r/(name+'.log')).open('w')as out,(r/(name+'.err')).open('w')as err:
  subprocess.run([str(r/'tool/target/release/value_prefilter'),str(ops),str(first),str(count),'2',str(r/(name+'.jsonl')),str(model),str(look)],env=env,stdout=out,stderr=err,check=True)
 whole=time.monotonic()-started
 rows=sorted(map(json.loads,(r/(name+'.jsonl')).read_text().splitlines()),key=lambda x:x['nonce'])
 assert len(rows)==count and [x['nonce']for x in rows]==list(range(first,first+count))
 assert all(x['proof_accepted']is False and x['authoritative_rejection']is False for x in rows)
 error=(r/(name+'.err')).read_text();assert 'CANDIDATE_OWN_FIAT_PROTECTED_4096_BYTE_CONTROLS_PASS' in error
 if force:assert error.count('FORCED_SCHEDULER_PROTECTED_KIND_PASS')==count
 if full:
  for marker in ['EARLY_FULLSTATE_AND_PHYSICAL_RNG9024_PASS','FIXED445_GUARD_CONDITIONAL_KNOWN_BITS_PASS','FUSED_GUARD_FIXED445_AUDIT32_PARTIAL_POLARITY_PASS']:assert marker in error
 if fused or shadow:assert 'FUSED_GUARD_LINEAGE_BOUND' in error or force
 wall=float(re.search(r'wall_seconds=([0-9.]+)',(r/(name+'.log')).read_text())[1])
 reports.append({'name':name,'fused_guard':fused,'benchmark_wall_seconds':wall,'subprocess_with_startup_seconds':whole,'rows':count,'complete_rows_match_prior':True})
 return rows,wall
for name,first,count,look,force in [('forced2',1,2,1,True),('shadow128',1,128,128,False),('partial11',17,11,9,False)]:
 raw,_=run(name+'-raw',first,count,look,False,not force,name=='shadow128',force)
 fused,_=run(name+'-fused',first,count,look,True,not force,name=='shadow128',force)
 assert raw==fused
 if force:assert raw==prior('forced2-generic')
 else:assert raw==prior('shadow128-generic'if name=='shadow128'else'partial-generic')
times={'raw':[],'fused':[]}
for trial in range(3):
 for mode in (['raw','fused']if trial%2==0 else['fused','raw']):
  rows,wall=run(f'{mode}-{trial}',1,4096,4096,mode=='fused');assert rows==reference
  times[mode].append(wall)
result={'status':'DISABLED_OPTIONAL_FUSED_GUARD_REPAIRED67_FULL_ROWS_AND_PROTECTED_CONTROLS_PASS',
 'candidate_stream_sha256':'0beec42b117e5f623736c4171e156d8ffdfaeeb585285636f91bab2838e7c10b',
 'precursor_archive_sha256':'db095518788bfafb6cdf0ded3a1172a9e570a14988e48a502d13ab76d71d70f0',
 'times_seconds':times,'median_seconds':{k:statistics.median(v)for k,v in times.items()},'trials':reports,
 'all4096rows_equal_prior_completed_rows':True,'fixed445_audit32_partial_and_polarity_controls':True,
 'full9024_q_b_phase_physical_MR_equality':True,'forced_scheduler_nonce1_2_protected_kind_equality':True,
 'generic_original_zeroIR_unchanged_both_modes':True,'classical_ids_u32_workspace66245':True,
 'resolved_scalar_library_sha256':'3bb2304219fb336795ea88d4bf81174883cdd33702f5975819b812c3dffca30f',
 'proof_accepted':False,'authoritative_rejection':False,'nonce_selected':None,'production_operational_changed':False,
 'cost_scope':'Two-thread isolated qualification only; no fourprocess/eightthread throughput, expected search time or launch authority.'}
(r/'RESULT.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps(result))
