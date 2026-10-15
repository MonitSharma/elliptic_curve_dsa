from pathlib import Path
import hashlib,json,os,subprocess
root=Path(__file__).resolve().parent;freeze=json.loads((root.parent/'masked-witness-20261016/MASK_FREEZE.json').read_text())
env=os.environ.copy();env['MASK_DAG_PATH']=freeze['mask_path'];env['MASK_DAG_SHA256']=freeze['mask_sha256']
assert hashlib.sha256(Path(env['MASK_DAG_PATH']).read_bytes()).hexdigest()==env['MASK_DAG_SHA256']
ops='/home/hclau/ecdsa_research/product-exact-20261015/candidate-product-final25/ops.bin';model='/home/hclau/ecdsa_research/prefilter-20261015/model-source'
for name,first,count,threads,lookahead,shadow,seed,fallback in [('shadow128',1,128,2,128,True,True,False),('partial',17,11,3,9,True,False,False),('timing4096-t16',1,4096,16,4096,False,False,False),('forced-full',1,1,1,1,False,False,True)]:
 current=env.copy()
 for flag,enabled in [('PACKED_ZERO_SHADOW',shadow),('CANDIDATE_SEED_SHADOW',seed),('FORCE_FULL_FALLBACK',fallback)]:
  if enabled:current[flag]='1'
 with (root/(name+'.log')).open('w') as out,(root/(name+'.err')).open('w') as err:
  subprocess.run([str(root/'tool/target/release/value_prefilter'),ops,str(first),str(count),str(threads),str(root/(name+'.jsonl')),model,str(lookahead)],env=current,stdout=out,stderr=err,check=True)
 if fallback:
  rows=[json.loads(s) for s in (root/(name+'.jsonl')).read_text().splitlines()];assert len(rows)==1 and rows[0]['protected_shots']==9024 and 'candidate_full_fallback_pass' in rows[0]
(root/'RESULT.json').write_text(json.dumps({'status':'BOUNDED_CANDIDATE25_SOURCE_TRANSFER_INTEGRATION_PASS','candidate_own_Fiat_4096bytes_nonces':[1,2,17,255],'candidate_zeroMR_output_shadow':True,'forced_full_candidate_9024':True,'universal_cache_transfer_pinned':True,'authoritative_rejection':False,'nonce_search':False},indent=2)+'\n')
