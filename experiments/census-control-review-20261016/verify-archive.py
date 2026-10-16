from pathlib import Path
import hashlib,json,tarfile
r=Path(__file__).resolve().parent;p=r/'review-v1.tar.gz';receipt=json.loads((r/'archive-receipt.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest();assert sha(p.read_bytes())==receipt['sha256']
with tarfile.open(p)as tf:
 m=json.load(tf.extractfile('MANIFEST.json'))
 for name,v in m['files'].items():
  b=tf.extractfile(name).read();assert len(b)==v['bytes']and sha(b)==v['sha256'],name
out=dict(status='PASS',archive_sha256=receipt['sha256'],verified_members=len(m['files']),external_server_only=len(m['external']))
(r/'verified-manifest.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
