from pathlib import Path
import hashlib,json,tarfile,shutil
b=Path('/home/hclau/ecdsa_research');r=b/'census-preseed-family-20261016';d=r/'source-only-v1';assert(r/'inventory.exit').read_text().strip()=='0';d.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['PREDECLARATION.json','MEMBERS10.json','RETAINED134.json','SUMMARY.json','INPUT-PINS.json','preseed-family.py','run-preseed-family.sh','inventory.log','inventory.exit','inventory.pid','script-before.sha256','script-after.sha256','started.utc','finished.utc']:
 shutil.copy2(r/name,d/name)
assert(r/'script-before.sha256').read_bytes()==(r/'script-after.sha256').read_bytes()
refs=[b/'census-deletion-family-20261016/source-only-v1.tar.gz',b/'census-control-review-20261016/review-v1.tar.gz',b/'current-value-attribution-20261016/seed-diagnosis-v1.tar.gz'];pins={str(p):sha(p)for p in refs};(d/'BASE-PINS.json').write_text(json.dumps(dict(pins=pins,seed_diagnosis_reference_scope='Named source helper boundary binding only. Its original2a scratch-zero proof is NOT transferred to changed prefix.'),indent=2)+'\n')
external={}
for name,digest in json.loads((r/'INPUT-PINS.json').read_text())['before'].items():
 p=Path(name)
 if p.suffix=='.bin':external[name]=dict(bytes=p.stat().st_size,sha256=digest,status='server-only, not archive member')
 else:shutil.copy2(p,d/p.name)
files={str(p.relative_to(d)):dict(bytes=p.stat().st_size,sha256=sha(p))for p in d.rglob('*')if p.is_file()};(d/'MANIFEST.json').write_text(json.dumps(dict(files=files,base_pins=pins,external=external),indent=2)+'\n');a=r/'source-only-v1.tar.gz'
with tarfile.open(a,'w:gz')as tf:tf.add(d,arcname=d.name)
with tarfile.open(a)as tf:
 for name,v in files.items():data=tf.extractfile(d.name+'/'+name).read();assert len(data)==v['bytes']and hashlib.sha256(data).hexdigest()==v['sha256']
receipt=dict(status='PASS',archive=str(a),sha256=sha(a),verified_members=len(files),external_streams=len(external));(r/'archive-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
