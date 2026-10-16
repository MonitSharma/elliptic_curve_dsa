from pathlib import Path
import json,hashlib,tarfile,shutil
r=Path('/home/hclau/ecdsa_research/census-control-review-20261016'); d=r/'native-review-v2'; d.mkdir(); sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert (r/'native-byte-review.exit').read_text().strip()=='0'
for name in ['review-native.py','native-byte-review.log','native-byte-review.exit','NATIVE-BYTE-REVIEW.json','NATIVE-SOURCE-REVIEW.json','REVIEW.json','SOURCE-ROW-PINS.json','CORE70.json']:
 shutil.copy2(r/name,d/name)
base=r/'review-v1.tar.gz'; pins={str(base):sha(base)}; (d/'BASE-PINS.json').write_text(json.dumps(pins,indent=2)+'\n')
files={str(p.relative_to(d)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in d.iterdir() if p.is_file()}; (d/'MANIFEST.json').write_text(json.dumps(dict(files=files,base_pins=pins),indent=2)+'\n'); a=r/'native-review-v2.tar.gz'
with tarfile.open(a,'w:gz') as tf:tf.add(d,arcname=d.name)
with tarfile.open(a) as tf:
 for name,v in files.items():data=tf.extractfile(d.name+'/'+name).read();assert len(data)==v['bytes'] and hashlib.sha256(data).hexdigest()==v['sha256']
receipt=dict(status='PASS',archive=str(a),sha256=sha(a),verified_members=len(files)); (r/'native-review-v2-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
