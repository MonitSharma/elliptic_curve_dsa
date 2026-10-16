from pathlib import Path
import json,hashlib,tarfile
r=Path(__file__).resolve().parent;sha=lambda b:hashlib.sha256(b).hexdigest();a=r/'native-base-evidence-v1.tar.gz';receipt=json.loads((r/'native-base-evidence-v1-receipt.json').read_text());assert sha(a.read_bytes())==receipt['sha256']
with tarfile.open(a)as tf:
 m=json.load(tf.extractfile('native-base-evidence-v1/MANIFEST.json'))
 for name,v in m['files'].items():
  data=tf.extractfile('native-base-evidence-v1/'+name).read();assert len(data)==v['bytes']and sha(data)==v['sha256'],name
 for name,digest in m['base_pins'].items():
  p=Path(name);assert sha((r.parent/p.parent.name/p.name).read_bytes())==digest
out=dict(status='PASS',archive_sha256=receipt['sha256'],verified_members=len(m['files']),base_pins_verified=len(m['base_pins']),external_streams=len(m['external']));(r/'native-base-local-verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
