"""Portable path/key correction; preserve original frozenmanifest and every original byte."""
from pathlib import Path
import json,hashlib,datetime
p=Path(__file__).parent;prior=p/'checkpoint-final-product-manifest.json';old=json.loads(prior.read_text());rows=[]
for r in old['files']:
 f=Path(r['path']);assert hashlib.sha256(f.read_bytes()).hexdigest()==r['raw_sha256'];q=dict(r);q['path']='experiments/'+r['path'].split('/experiments/',1)[1];q['sha256']=q['expected_gitblob_sha256'];rows.append(q)
for name in ['repair57-freeze-v2.py','repair57-sixteen-preparation-failure-transcript.txt']:
 f=p/name;b=f.read_bytes();g=b.replace(b'\r\n',b'\n');rows.append({'path':'experiments/overnight-20261014/product/'+name,'bytes':len(b),'raw_sha256':hashlib.sha256(b).hexdigest(),'expected_gitblob_sha256':hashlib.sha256(g).hexdigest(),'sha256':hashlib.sha256(g).hexdigest(),'hash_scope':'UTF8_LF_Gitblob'})
old.update({'prepared_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_manifest_sha256':hashlib.sha256(prior.read_bytes()).hexdigest(),'portability_correction':'Paths made repository-relative and sha256 aliases expectedGitblob; originalmanifest and all126originalfiles unchanged. Added originalfailedpreparation tool-output excerpt and this generator.','files':rows})
(p/'checkpoint-final-product-manifest-v2.json').write_text(json.dumps(old,indent=2)+'\n',newline='\n');print('FROZEN_PORTABLE',len(rows))
