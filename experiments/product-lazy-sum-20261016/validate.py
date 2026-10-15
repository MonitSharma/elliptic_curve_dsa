from pathlib import Path
import json,os,subprocess
root=Path(__file__).resolve().parent;ops='/home/hclau/ecdsa_research/product-exact-20261015/candidate-product-final25/ops.bin';model='/home/hclau/ecdsa_research/prefilter-20261015/model-source'
def run(name,first,count,threads,look,extra):
 env=os.environ.copy();env['DEFER_EXPECTED_SUMS']='1';env.update(extra)
 with (root/(name+'.log')).open('w') as out,(root/(name+'.err')).open('w') as err:subprocess.run([str(root/'tool/target/release/value_prefilter'),ops,str(first),str(count),str(threads),str(root/(name+'.jsonl')),model,str(look)],env=env,stdout=out,stderr=err,check=True)
 rows=sorted(map(json.loads,(root/(name+'.jsonl')).read_text().splitlines()),key=lambda r:r['nonce']);assert len(rows)==count and [r['nonce'] for r in rows]==list(range(first,first+count));assert all(not r['authoritative_rejection'] and not r['proof_accepted'] for r in rows);return rows
rows=run('full9024',1,1,1,1,{'DEFER_SUM_SHADOW':'1','EARLY_FULLSTATE_SHADOW':'1','FORCE_FULL_FALLBACK':'1'})
reference=sorted(map(json.loads,(root.parent/'product-early-filter-20261016/fullstate9024.jsonl').read_text().splitlines()),key=lambda r:r['nonce']);assert rows==reference
for name,first,count,look in [('shadow128',1,128,128),('partial',17,11,9)]:
 rows=run(name,first,count,1,look,{'PACKED_ZERO_SHADOW':'1'})
 reference=sorted(map(json.loads,(root.parent/'product-fused-filter-20261016'/(name+'.jsonl')).read_text().splitlines()),key=lambda r:r['nonce']);assert rows==reference
rows=run('rows4096',1,4096,1,4096,{})
reference=sorted(map(json.loads,(root.parent/'product-early-filter-20261016/rows4096.jsonl').read_text().splitlines()),key=lambda r:r['nonce']);assert rows==reference
report={'status':'DISABLED_LAZY_SUM_FULL_PACKET_READY_FALLBACK_SHADOW_AND_ROWS_PASS','all9024_triples_and_final_reader_equal':True,'partial11_triples_equal':True,'protected9024_every_q_b_phase_and_MR_equal':True,'forced_fallback_disposition_equal':True,'shadow128_and_partial':True,'all4096_rows_equal':True,'authoritative_rejection':False,'nonce_selected':None,'production_changed':False}
(root/'VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
