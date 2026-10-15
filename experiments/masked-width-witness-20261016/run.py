from pathlib import Path
import hashlib,json,os,subprocess
root=Path(__file__).resolve().parent;freeze=json.loads((root.parent/'masked-witness-20261016/MASK_FREEZE.json').read_text())
assert freeze['status']=='TERMINAL_EXPORT_REVIEWED_FOR_BOUNDED_BENCHMARK_ONLY'
env=os.environ.copy();env['MASK_DAG_PATH']=freeze['mask_path'];env['MASK_DAG_SHA256']=freeze['mask_sha256']
assert hashlib.sha256(Path(env['MASK_DAG_PATH']).read_bytes()).hexdigest()==env['MASK_DAG_SHA256']
ops='/home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin';model='/home/hclau/ecdsa_research/prefilter-20261015/model-source'
for name,first,count,threads,lookahead,shadow in [('shadow128',1,128,2,128,True),('partial',17,11,3,9,True),('timing1024-t16',1,1024,16,1024,False),('timing4096-t16',1,4096,16,4096,False),('timing4096-t32',1,4096,32,4096,False),('positive',1046072871510,1,2,1,False)]:
 current=env.copy()
 if shadow:current['PACKED_ZERO_SHADOW']='1'
 with (root/(name+'.log')).open('w') as out,(root/(name+'.err')).open('w') as err:
  subprocess.run([str(root/'tool/target/release/value_prefilter'),ops,str(first),str(count),str(threads),str(root/(name+'.jsonl')),model,str(lookahead)],env=current,stdout=out,stderr=err,check=True)
 if name=='positive':
  rows=[json.loads(s) for s in (root/(name+'.jsonl')).read_text().splitlines()];assert len(rows)==1 and rows[0]['original_full_fallback_pass'] and rows[0]['protected_shots']==9024
for name in ['shadow128','partial','timing1024-t16']:
 old=root.parent/'masked-witness-20261016'/({'timing1024-t16':'timing-t16'}.get(name,name)+'.jsonl')
 a=sorted(map(json.loads,old.read_text().splitlines()),key=lambda r:r['nonce']);b=sorted(map(json.loads,(root/(name+'.jsonl')).read_text().splitlines()),key=lambda r:r['nonce']);assert a==b,name
(root/'RESULT.json').write_text(json.dumps({'status':'BOUNDED_WIDTH_ADAPTIVE_INTEGRATION_PASS','original_v3_rows_identical':True,'positive_9024':True,'nonce_search':False,'authoritative_rejection':False},indent=2)+'\n')
