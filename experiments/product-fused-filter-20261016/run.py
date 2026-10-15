from pathlib import Path
import json,os,subprocess
root=Path(__file__).resolve().parent
ops='/home/hclau/ecdsa_research/product-exact-20261015/candidate-product-final25/ops.bin';model='/home/hclau/ecdsa_research/prefilter-20261015/model-source'
for name,first,count,threads,lookahead,shadow in [('shadow128',1,128,2,128,True),('partial',17,11,3,9,True),('timing4096-t16',1,4096,16,4096,False)]:
 env=os.environ.copy()
 if shadow:env['PACKED_ZERO_SHADOW']='1'
 with (root/(name+'.log')).open('w') as out,(root/(name+'.err')).open('w') as err:subprocess.run([str(root/'tool/target/release/value_prefilter'),ops,str(first),str(count),str(threads),str(root/(name+'.jsonl')),model,str(lookahead)],env=env,stdout=out,stderr=err,check=True)
 old=root.parent/'product-mask-filter-20261016'/(name+'.jsonl');a=sorted(map(json.loads,old.read_text().splitlines()),key=lambda r:r['nonce']);b=sorted(map(json.loads,(root/(name+'.jsonl')).read_text().splitlines()),key=lambda r:r['nonce']);assert a==b,name
(root/'RESULT.json').write_text(json.dumps({'status':'FUSED_CANDIDATE25_BOUNDED_ROWS_EXACT_PASS','candidate_zeroMR_shadow128_and_partial':True,'all4096witness_rows_equal_unfused':True,'nonce_selected':False,'authoritative_rejection':False},indent=2)+'\n')
