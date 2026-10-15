from pathlib import Path
import json,hashlib,tarfile,shutil
r=Path('/home/hclau/ecdsa_research/n2-loan-retention-20261016');n='source-only-retention-v1';d=r/n;assert not d.exists();d.mkdir()
for p in r.iterdir():
 if p.is_file() and p.suffix in ['.py','.sh','.json','.log','.exit','.patch'] and p.name!='collect-retention.py':shutil.copy2(p,d/p.name)
for src in ['all-retained','all-retained-cap8']:
 for p in (r/src/'src/point_add').rglob('*'):
  if p.is_file():q=d/src/'src/point_add'/p.relative_to(r/src/'src/point_add');q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
sha=lambda b:hashlib.sha256(b).hexdigest()
manifest={str(p.relative_to(d)):dict(bytes=p.stat().st_size,sha256=sha(p.read_bytes()))for p in d.rglob('*')if p.is_file()}
(d/'MANIFEST.json').write_text(json.dumps(dict(files=manifest,status='SOURCE-ONLY NEGATIVE; no complete native candidate or census',original_cap='capacity failure with ALL loans disabled',scoped_plus8='raw builder completes Q1242, raw deltaT0; original y42_bound anchor rejects; never bypassed'),indent=2)+'\n')
p=r/(n+'.tar.gz')
with tarfile.open(p,'w:gz')as tf:tf.add(d,arcname=n)
with tarfile.open(p)as tf:
 for f,v in manifest.items():b=tf.extractfile(n+'/'+f).read();assert sha(b)==v['sha256'] and len(b)==v['bytes']
out=dict(status='PASS',archive=str(p),sha256=sha(p.read_bytes()),bytes=p.stat().st_size,verified_members=len(manifest));(r/(n+'-receipt.json')).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
