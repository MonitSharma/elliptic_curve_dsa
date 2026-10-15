from pathlib import Path
import hashlib,json,tarfile
root=Path(__file__).resolve().parent
paths=[p for p in (root/'evidence').rglob('*') if p.is_file() and p.suffix!='.bin']
paths += [p for p in root.iterdir() if p.is_file() and p.suffix in ['.py','.sh','.md','.log','.exit','.json','.sha256'] and p.name not in ['manifest.json','verified-manifest.json']]
paths=sorted(set(paths));manifest={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
(root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(root/'evidence.tar.gz','w:gz') as t:
 for p in paths+[root/'manifest.json']:t.add(p,arcname=str(p.relative_to(root)))
print('Bundled',len(paths),'artifacts')
