"""Bundle named research evidence, excluding streams, binaries and credentials."""
from pathlib import Path
import hashlib
import json
import tarfile
root=Path(__file__).resolve().parent
paths=[]
for directory in ['evidence','sweep','extra','intern','single']:
 for p in (root/directory).rglob('*'):
  if p.is_file() and p.suffix not in ['.bin'] and p.name not in ['build_circuit','paired_diagnostic']:
   paths.append(p)
for pattern in ['*.py','*.sh','*.rs','*.exit','*.log','*.md']:
 paths.extend(root.glob(pattern))
paths=sorted(set(paths))
manifest={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
(root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(root/'evidence.tar.gz','w:gz') as archive:
 for p in paths+[root/'manifest.json']:
  archive.add(p,arcname=str(p.relative_to(root)))
print(f'Bundled {len(paths)} artifacts; frozen binary streams stay on server.')
