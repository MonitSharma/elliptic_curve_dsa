from pathlib import Path
import json,hashlib,tarfile,shutil
b=Path('/home/hclau/ecdsa_research');r=b/'census-deletion-n2-join-20261016';d=r/'source-only-v1';assert(r/'join.exit').read_text().strip()=='0';d.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['PREDECLARATION.json','ALL74-JOIN-SOURCES.json','ALL-BOUNDARIES.json','SUMMARY.json','INPUT-PINS.json','join-deletions-n2.py','run-deletion-join.sh','join.log','join.exit','join.pid','started.utc','finished.utc','script-before.sha256','script-after.sha256']:
 shutil.copy2(r/name,d/name)
assert(r/'script-before.sha256').read_bytes()==(r/'script-after.sha256').read_bytes();shutil.copytree(r/'initial-null-carry-negative',d/'initial-null-carry-negative')
refs=[b/'census-deletion-family-20261016/source-only-v1.tar.gz',b/'current-value-attribution-20261016/attribution-checkpoint-v1.tar.gz',b/'current-value-attribution-20261016/all-add-attribution-addendum-v3.tar.gz'];pins={str(p):sha(p)for p in refs};(d/'BASE-PINS.json').write_text(json.dumps(pins,indent=2)+'\n')
inputs=json.loads((r/'INPUT-PINS.json').read_text())['before'];external={}
for name,digest in inputs.items():
 p=Path(name)
 if p.suffix=='.bin':external[name]=dict(sha256=digest,bytes=p.stat().st_size,status='server-only, not archive member')
 else:shutil.copy2(p,d/p.name)
files={str(p.relative_to(d)):dict(bytes=p.stat().st_size,sha256=sha(p))for p in d.rglob('*')if p.is_file()};(d/'MANIFEST.json').write_text(json.dumps(dict(files=files,base_pins=pins,external=external),indent=2)+'\n');a=r/'source-only-v1.tar.gz'
with tarfile.open(a,'w:gz')as tf:tf.add(d,arcname=d.name)
with tarfile.open(a)as tf:
 for name,v in files.items():data=tf.extractfile(d.name+'/'+name).read();assert len(data)==v['bytes']and hashlib.sha256(data).hexdigest()==v['sha256']
receipt=dict(status='PASS',archive=str(a),sha256=sha(a),verified_members=len(files),external_streams=len(external));(r/'archive-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
