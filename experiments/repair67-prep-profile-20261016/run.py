from pathlib import Path
import os,json,subprocess,time,tarfile,hashlib,re
r=Path(__file__).resolve().parent;old=r.parent/'repair67-fused-filter-20261016'
archive=old/'evidence.tar.gz';assert hashlib.sha256(archive.read_bytes()).hexdigest()=='7af8c67adb7698f01a43af981b8f1a6c78930d1178dc65ac5fbc69bbcf2de85b'
with tarfile.open(archive)as t:reference=sorted(map(json.loads,t.extractfile('fused-0.jsonl').read().decode().splitlines()),key=lambda x:x['nonce'])
records=[]
for mode in ['off','on']:
 env=os.environ.copy()
 for key in ['PROFILE_PREP','SCALAR_FAST_LIB','FAST_ZERO_DISPATCH','RAIL_SHADOW','PACKED_ZERO_SHADOW','EARLY_FULLSTATE_SHADOW','FIXED_TRANSFER_SHADOW','FORCE_FULL_FALLBACK','FUSED_GUARD_SHADOW']:env.pop(key,None)
 env.update(FUSED_GUARD='1',CANDIDATE_SEED_SHADOW='1')
 if mode=='on':env['PROFILE_PREP']='1'
 start=time.monotonic()
 with(r/(mode+'.log')).open('w')as out,(r/(mode+'.err')).open('w')as err:
  subprocess.run([str(r/'tool/target/release/value_prefilter'),str(r.parent/'product-exact-20261015/repair-to67-rank-20261016/repair-67-retained-1024-proxy.bin'),'1','4096','2',str(r/(mode+'.jsonl')),str(r.parent/'prefilter-20261015/model-source'),'4096'],env=env,stdout=out,stderr=err,check=True)
 elapsed=time.monotonic()-start
 rows=sorted(map(json.loads,(r/(mode+'.jsonl')).read_text().splitlines()),key=lambda x:x['nonce']);assert rows==reference and len(rows)==4096
 assert all(x['proof_accepted']is False and x['authoritative_rejection']is False for x in rows)
 error=(r/(mode+'.err')).read_text();assert 'CANDIDATE_OWN_FIAT_PROTECTED_4096_BYTE_CONTROLS_PASS' in error
 wall=float(re.search(r'wall_seconds=([0-9.]+)',(r/(mode+'.log')).read_text())[1])
 row={'mode':mode,'process_wall_seconds':elapsed,'window_wall_seconds':wall,'outside_window_wall_seconds':elapsed-wall,'all4096_rows_match_frozen_precursor':True}
 marker=[line[len('PREP_PROFILE_JSON '):]for line in error.splitlines()if line.startswith('PREP_PROFILE_JSON ')]
 if mode=='on':assert len(marker)==1;row['profile']=json.loads(marker[0])
 else:assert not marker
 records.append(row)
result={'status':'BOUNDED_INSTRUMENTATION_OWN_FIAT_AND_COMPLETE4096_ROWS_PASS','records':records,'new_sampling':False,'source_operations_or_libraries_changed':False,'proof_accepted':False,'cost_forecast_or_search_authority':False,'measurement_limits':'One off/on fixed pair; startup and diagnostic controls separated, summed worker times overlap and are not aggregate wall time; no stable throughput or instrumentation-overhead claim.'}
(r/'RESULT.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps(result))
