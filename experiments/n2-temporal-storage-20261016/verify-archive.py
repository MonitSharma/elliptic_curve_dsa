from pathlib import Path
import hashlib,json,tarfile
r=Path(__file__).resolve().parent; p=r/'source-only-temporal-v1.tar.gz'; receipt=json.loads((r/'archive-receipt.json').read_text()); sha=lambda d:hashlib.sha256(d).hexdigest(); assert sha(p.read_bytes())==receipt['sha256']
with tarfile.open(p) as tf:
 prefix='source-only-temporal-v1/'; m=json.load(tf.extractfile(prefix+'MANIFEST.json'))
 for name,v in m['files'].items():
  data=tf.extractfile(prefix+name).read(); assert len(data)==v['bytes'] and sha(data)==v['sha256']
 for name,digest in m['base_pins'].items():
  local=r.parent/Path(name).parent.name/Path(name).name; assert sha(local.read_bytes())==digest
 out=dict(status='PASS',archive_sha256=receipt['sha256'],verified_members=len(m['files']),base_pins_verified=len(m['base_pins']),external_server_only=len(m['external']))
(r/'verified-manifest.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
