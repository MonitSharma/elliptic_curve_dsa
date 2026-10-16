from pathlib import Path
import hashlib,json,tarfile
r=Path(__file__).resolve().parent; receipt=json.loads((r/'native-review-v2-receipt.json').read_text()); sha=lambda x:hashlib.sha256(x).hexdigest(); a=r/'native-review-v2.tar.gz'; assert sha(a.read_bytes())==receipt['sha256']
with tarfile.open(a) as tf:
 m=json.load(tf.extractfile('native-review-v2/MANIFEST.json'))
 for name,v in m['files'].items():
  data=tf.extractfile('native-review-v2/'+name).read(); assert sha(data)==v['sha256'] and len(data)==v['bytes']
 for name,digest in m['base_pins'].items(): assert sha((r/Path(name).name).read_bytes())==digest
out=dict(status='PASS',archive_sha256=receipt['sha256'],verified_members=len(m['files']),base_pins_verified=len(m['base_pins']));(r/'native-review-v2-local-verification.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
