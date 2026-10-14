from pathlib import Path
import hashlib,json,datetime
p=Path(__file__).parent;files=[]
for name in ['leader441d-review.md','leader441d-static-receipt.json','leader441d-actual-source.patch','leader441d-inspect.py','leader441d-freeze.py']:
 f=p/name;b=f.read_bytes();g=b if f.suffix=='.patch'else b.replace(b'\r\n',b'\n');files.append({'path':'experiments/overnight-20261014/product/'+name,'sha256':hashlib.sha256(g).hexdigest(),'raw_sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'hash_scope':'exactbinary'if f.suffix=='.patch'else'UTF8_LF_Gitblob'})
(p/'leader441d-review-manifest.json').write_text(json.dumps({'status':'FROZEN_READ_ONLY_PUBLIC_SOURCE_REVIEW','candidate_changes':False,'workloads_or_benchmarks':False,'qualified_local_score':None,'repair57_manifest_untouched':True,'prepared_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':files},indent=2)+'\n',newline='\n')
print('FROZEN_LEADER_SOURCE_REVIEW',len(files))
