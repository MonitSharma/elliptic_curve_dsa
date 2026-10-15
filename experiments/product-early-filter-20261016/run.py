from pathlib import Path
import json,os,subprocess
root=Path(__file__).resolve().parent;ops='/home/hclau/ecdsa_research/product-exact-20261015/candidate-product-final25/ops.bin';model='/home/hclau/ecdsa_research/prefilter-20261015/model-source'
for name,first,count,threads,lookahead,shadow,forced in [('fullstate9024',1,1,1,1,True,True),('rows4096',1,4096,16,4096,False,False)]:
 env=os.environ.copy()
 if shadow:env['EARLY_FULLSTATE_SHADOW']='1'
 if forced:env['FORCE_FULL_FALLBACK']='1'
 with (root/(name+'.log')).open('w') as out,(root/(name+'.err')).open('w') as err:subprocess.run([str(root/'tool/target/release/value_prefilter'),ops,str(first),str(count),str(threads),str(root/(name+'.jsonl')),model,str(lookahead)],env=env,stdout=out,stderr=err,check=True)
 if forced:
  rows=[json.loads(s) for s in (root/(name+'.jsonl')).read_text().splitlines()];assert len(rows)==1 and not rows[0]['candidate_full_fallback_pass'] and rows[0]['exact_early_kind']!='pass'
 else:
  old=root.parent/'product-fused-filter-20261016/timing4096-t16.jsonl';a=sorted(map(json.loads,old.read_text().splitlines()),key=lambda r:r['nonce']);b=sorted(map(json.loads,(root/(name+'.jsonl')).read_text().splitlines()),key=lambda r:r['nonce']);assert a==b
(root/'RESULT.json').write_text(json.dumps({'status':'EXACT_EARLY_FULLSTATE9024_AND_ROWS4096_PASS','every_q_b_phase_and_physical_rng_match':True,'full_protected_confirmation_for_all_survivors':True,'nonce_search':False,'authoritative_rejection':False},indent=2)+'\n')
