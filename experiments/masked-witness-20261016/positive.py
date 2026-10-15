from pathlib import Path
import hashlib,json,os,subprocess
root=Path(__file__).resolve().parent
freeze=json.loads((root/'MASK_FREEZE.json').read_text())
assert freeze['status']=='TERMINAL_EXPORT_REVIEWED_FOR_BOUNDED_BENCHMARK_ONLY'
env=os.environ.copy()
env['MASK_DAG_PATH']=freeze['mask_path'];env['MASK_DAG_SHA256']=freeze['mask_sha256']
assert hashlib.sha256(Path(env['MASK_DAG_PATH']).read_bytes()).hexdigest()==env['MASK_DAG_SHA256']
# This pre-existing original-source passing nonce is a fixed positive control.
with (root/'positive.log').open('w') as out,(root/'positive.err').open('w') as err:
 subprocess.run([str(root/'tool/target/release/value_prefilter'),'/home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin','1046072871510','1','2',str(root/'positive.jsonl'),'/home/hclau/ecdsa_research/prefilter-20261015/model-source','1'],env=env,stdout=out,stderr=err,check=True)
rows=[json.loads(s) for s in (root/'positive.jsonl').read_text().splitlines()]
assert len(rows)==1 and rows[0]['nonce']==1046072871510
assert rows[0]['original_full_fallback_pass'] and rows[0]['protected_shots']==9024
assert not rows[0]['authoritative_rejection'] and not rows[0]['proof_accepted']
(root/'POSITIVE-RESULT.json').write_text(json.dumps({'status':'FIXED_ORIGINAL_POSITIVE_9024_PASS','row':rows[0],'nonce_search':False},indent=2)+'\n')
