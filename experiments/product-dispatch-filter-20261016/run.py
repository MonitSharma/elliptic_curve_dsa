from pathlib import Path
import json,os,re,subprocess,statistics
root=Path(__file__).resolve().parent;ops='/home/hclau/ecdsa_research/product-exact-20261015/candidate-product-final25/ops.bin';model='/home/hclau/ecdsa_research/prefilter-20261015/model-source'
def run(name,first,count,threads,look,fast,shadow=False):
 env=os.environ.copy()
 if fast:env['FAST_ZERO_DISPATCH']='1'
 if shadow:env['PACKED_ZERO_SHADOW']='1'
 with (root/(name+'.log')).open('w') as out,(root/(name+'.err')).open('w') as err:
  subprocess.run([str(root/'tool/target/release/value_prefilter'),ops,str(first),str(count),str(threads),str(root/(name+'.jsonl')),model,str(look)],env=env,stdout=out,stderr=err,check=True)
 rows=sorted(map(json.loads,(root/(name+'.jsonl')).read_text().splitlines()),key=lambda r:r['nonce']);assert len(rows)==count and [r['nonce'] for r in rows]==list(range(first,first+count))
 assert all(not r['authoritative_rejection'] and not r['proof_accepted'] for r in rows)
 wall=float(re.search(r'wall_seconds=([0-9.]+)',(root/(name+'.log')).read_text())[1]);return rows,wall
for name,first,count,threads,look in [('shadow128',1,128,2,128),('partial',17,11,3,9)]:
 rows,wall=run(name,first,count,threads,look,True,True)
 old=root.parent/'product-fused-filter-20261016'/(name+'.jsonl');assert rows==sorted(map(json.loads,old.read_text().splitlines()),key=lambda r:r['nonce'])
reference=sorted(map(json.loads,(root.parent/'product-early-filter-20261016/rows4096.jsonl').read_text().splitlines()),key=lambda r:r['nonce'])
times={'baseline':[],'threaded':[]}
for trial in range(3):
 for mode in (['baseline','threaded'] if trial%2==0 else ['threaded','baseline']):
  rows,wall=run(f'{mode}-{trial}',1,4096,8,4096,mode=='threaded');assert rows==reference
  times[mode].append(wall)
report={'status':'DISABLED_FULL_PIPELINE_ROWS_AND_SHADOW_PASS','times_seconds':times,'median_seconds':{mode:statistics.median(ts) for mode,ts in times.items()},'all4096_rows_identical':True,'protected_zeroMR_shadow128_and_partial':True,'authoritative_rejection':False,'nonce_selected':None,'production_changed':False}
(root/'RESULT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
