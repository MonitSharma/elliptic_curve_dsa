from pathlib import Path
import hashlib,json,os,subprocess,time
root=Path(__file__).resolve().parent
while not (root/'MASK_FREEZE.json').exists():time.sleep(2)
freeze=json.loads((root/'MASK_FREEZE.json').read_text());assert freeze['status']=='TERMINAL_EXPORT_REVIEWED_FOR_BOUNDED_BENCHMARK_ONLY'
env=os.environ.copy();env['MASK_DAG_PATH']=freeze['mask_path'];env['MASK_DAG_SHA256']=freeze['mask_sha256']
assert hashlib.sha256(Path(env['MASK_DAG_PATH']).read_bytes()).hexdigest()==env['MASK_DAG_SHA256']
ops='/home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin';model='/home/hclau/ecdsa_research/prefilter-20261015/model-source'
for name,first,count,workers,lookahead,shadow in [('shadow128',1,128,2,128,True),('timing-t2',1,1024,2,1024,False),('timing-t16',1,1024,16,1024,False),('partial',17,11,3,9,True)]:
 current=env.copy()
 if shadow:current['PACKED_ZERO_SHADOW']='1'
 with (root/(name+'.log')).open('w') as out,(root/(name+'.err')).open('w') as err:
  subprocess.run([str(root/'tool/target/release/value_prefilter'),ops,str(first),str(count),str(workers),str(root/(name+'.jsonl')),model,str(lookahead)],env=current,stdout=out,stderr=err,check=True)
(root/'completed.json').write_text(json.dumps({'status':'BOUNDED_MASKED_WITNESS_BENCHMARK_COMPLETED','authoritative_rejection':False,'nonce_search':False,'nonce_selected':False},indent=2)+'\n')
