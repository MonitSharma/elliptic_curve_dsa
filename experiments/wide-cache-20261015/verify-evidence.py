"""Hash-check the saved evidence archive without trusting member paths."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import tarfile
root=Path(__file__).resolve().parent
with tarfile.open(root/'evidence.tar.gz','r:gz') as archive:
 names=archive.getnames()
 assert len(names)==len(set(names))
 assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names)
 manifest=json.load(archive.extractfile('manifest.json'))
 for name, expected in manifest.items():
  data=archive.extractfile(name).read()
  assert hashlib.sha256(data).hexdigest()==expected,name
 for name in ['evidence/paired-summary.json','evidence/candidate.patch','evidence/stream.sha256','evidence/protected.sha256']:
  p=root/name
  p.parent.mkdir(parents=True,exist_ok=True)
  p.write_bytes(archive.extractfile(name).read())
(root/'verified-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(f'Verified {len(manifest)} archived artifacts.')
