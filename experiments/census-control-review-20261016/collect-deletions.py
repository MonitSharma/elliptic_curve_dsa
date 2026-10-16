from pathlib import Path
import json,hashlib,tarfile,shutil
b=Path('/home/hclau/ecdsa_research');r=b/'census-deletion-family-20261016';d=r/'source-only-v1';assert (r/'inventory.exit').read_text().strip()=='0';d.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['PREDECLARATION.json','ALL74.json','SUMMARY.json','INPUT-PINS.json','inventory-deletions.py','run-deletions.sh','inventory.log','inventory.exit','inventory.pid','started.utc','finished.utc','script-before.sha256','script-after.sha256']:
 shutil.copy2(r/name,d/name)
assert (r/'script-before.sha256').read_bytes()==(r/'script-after.sha256').read_bytes()
refs=[b/'census-control-review-20261016/ALL144.json',b/'census-control-review-20261016/census_cut_data.txt',b/'census-control-review-20261016/review-v1.tar.gz',b/'census-control-review-20261016/native-review-v2.tar.gz']
for p in refs[:2]:shutil.copy2(p,d/p.name)
pins={str(p):sha(p) for p in refs[2:]};(d/'BASE-PINS.json').write_text(json.dumps(pins,indent=2)+'\n')
inputs=json.loads((r/'INPUT-PINS.json').read_text())['before']; external={name:dict(sha256=digest,bytes=Path(name).stat().st_size,status='server-only, not archive member') for name,digest in inputs.items() if name.endswith('ops.bin') or name.endswith('before-census.bin')}
# Full markers are included to permit root-independent diagnostic family checks.
for name in ['actual-markers.json','actual-add-markers.json']:
 shutil.copy2(b/'current-value-attribution-20261016'/name,d/name)
files={str(p.relative_to(d)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in d.iterdir() if p.is_file()};(d/'MANIFEST.json').write_text(json.dumps(dict(files=files,base_pins=pins,external=external),indent=2)+'\n');a=r/'source-only-v1.tar.gz'
with tarfile.open(a,'w:gz')as tf:tf.add(d,arcname=d.name)
with tarfile.open(a)as tf:
 for name,v in files.items():data=tf.extractfile(d.name+'/'+name).read();assert len(data)==v['bytes'] and hashlib.sha256(data).hexdigest()==v['sha256']
receipt=dict(status='PASS',archive=str(a),sha256=sha(a),verified_members=len(files),external_streams=len(external));(r/'archive-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
