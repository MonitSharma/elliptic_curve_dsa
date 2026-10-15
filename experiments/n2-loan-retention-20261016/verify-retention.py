from pathlib import Path
import json,hashlib,tarfile
r=Path(__file__).resolve().parent;n='source-only-retention-v1';p=r/(n+'.tar.gz');receipt=json.loads((r/(n+'-receipt.json')).read_text());sha=lambda b:hashlib.sha256(b).hexdigest();assert sha(p.read_bytes())==receipt['sha256']
with tarfile.open(p)as tf:
 m=json.load(tf.extractfile(n+'/MANIFEST.json'))
 for f,v in m['files'].items():
  b=tf.extractfile(n+'/'+f).read();assert len(b)==v['bytes'] and sha(b)==v['sha256'],f
out=dict(status='PASS',archive=str(p.resolve()),sha256=receipt['sha256'],verified_members=len(m['files']),source_only_negative=True)
(r/(n+'-local-verification.json')).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
