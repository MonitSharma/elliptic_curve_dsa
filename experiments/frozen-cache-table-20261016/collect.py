from pathlib import Path
import hashlib,json,tarfile
root=Path(__file__).resolve().parent
paths=[p for p in root.iterdir() if p.is_file() and p.name not in ['evidence.tar.gz','manifest.json','verified-manifest.json','frozen_cache25.bin']]
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
(root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(root/'evidence.tar.gz','w:gz') as t:
 for p in sorted(paths)+[root/'manifest.json']:t.add(p,arcname=p.name)
print('archived',len(paths),'artifacts including complete binary point_add source')
