from pathlib import Path
import hashlib,json,tarfile
r=Path(__file__).resolve().parent;n='phase-attribution-addendum-v2';p=r/(n+'.tar.gz')
receipt=json.loads((r/(n+'-receipt.json')).read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(p.read_bytes())==receipt['sha256']
with tarfile.open(p) as tf:
 m=json.load(tf.extractfile(n+'/MANIFEST.json'))
 for f,v in m['files'].items():
  b=tf.extractfile(n+'/'+f).read();assert len(b)==v['bytes'] and sha(b)==v['sha256'],f
 assert m['depends_on']['base_sha256']==sha((r/'attribution-checkpoint-v1.tar.gz').read_bytes())
out=dict(status='PASS',archive=str(p.resolve()),sha256=receipt['sha256'],verified_members=len(m['files']),base_checkpoint_sha256=m['depends_on']['base_sha256'])
(r/(n+'-local-verification.json')).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
