from pathlib import Path
import tarfile,json,hashlib
root=Path(__file__).resolve().parent
files=[]
for p in root.rglob('*'):
 if not p.is_file()or'target'in p.parts or p.suffix=='.bin' or p.name.endswith('.tar.gz'):continue
 rel=p.relative_to(root)
 if rel.parts[0]=='tip-before' and not str(rel).startswith('tip-before/src/point_add/'):continue
 files.append(p)
manifest={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()for p in files}
(root/'terminal-source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(root/'terminal-evidence.tar.gz','w:gz')as tar:
 for p in files+[root/'terminal-source-manifest.json']:tar.add(p,arcname=str(p.relative_to(root)))
print(hashlib.sha256((root/'terminal-evidence.tar.gz').read_bytes()).hexdigest())
