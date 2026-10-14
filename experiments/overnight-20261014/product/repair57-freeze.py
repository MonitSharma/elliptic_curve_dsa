"""Freeze completed product final evidence; no active variants enter this manifest."""
from pathlib import Path
import hashlib,json,datetime
p=Path(__file__).parent;rows=[]
for f in sorted(p.glob('repair57-*')):
 if not f.is_file():continue
 b=f.read_bytes();binary=f.suffix in['.gz','.patch'];git=b if binary else b.replace(b'\r\n',b'\n')
 rows.append({'path':f.as_posix(),'bytes':len(b),'raw_sha256':hashlib.sha256(b).hexdigest(),'expected_gitblob_sha256':hashlib.sha256(git).hexdigest(),'hash_scope':'exactbinary' if binary else 'UTF8_LF_Gitblob'})
r={'prepared_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'FINAL_COMPLETED_PRODUCT_REPAIR_SCIENCE_FROZEN','qualified_score':None,'active_product_pids':[],'scope':'Completed exact104 fold, roomy body, exactproduction body,16 actual interfaces and16 literal originalprefix states; unchangedANFcap inconclusive, correctedBDD allfutureMR/native, invalidzero-test target andfullsourceallocator111 fatal preserved. No fullrepair/record/score/sourceadapter.','files':rows}
(p/'checkpoint-final-product-manifest.json').write_text(json.dumps(r,indent=2)+'\n',newline='\n');print('FROZEN',len(rows),'files',sum(r['bytes']for r in rows),'bytes')
