from pathlib import Path
import tarfile,hashlib,json
p=Path(__file__).resolve().parent/'evidence-a29-conditional-transfer.tar.gz'
assert hashlib.sha256(p.read_bytes()).hexdigest()=='ce79b3d462f65bd1076da8e8c3c8ada831889e0f3999f297ead6ffbb0015c753'
with tarfile.open(p) as t:
 m=json.load(t.extractfile('MANIFEST.json'))
 for r in m['files']:
  assert hashlib.sha256(t.extractfile(r['path']).read()).hexdigest()==r['sha256']
print(json.dumps({'status':'ALL_TRANSFERRED_ARCHIVE_MEMBERS_VERIFY','files':len(m['files']),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}))
