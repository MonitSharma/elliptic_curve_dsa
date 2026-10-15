from pathlib import Path
import hashlib,json,tarfile
root=Path(__file__).resolve().parent
paths=[]
for p in root.iterdir():
 if p.is_file() and p.name!='manifest.json' and (p.suffix in ['.c','.h','.py','.sh','.log','.sha256','.tsv','.txt','.json','.jsonl','.rs','.exit','.md'] or p.name=='COPYING.secp256k1'):
  paths.append(p)
for sub in ['verify-reference','rail-tool']:
 for name in ['Cargo.toml','Cargo.lock']:
  if (root/sub/name).exists():paths.append(root/sub/name)
 paths.extend((root/sub/'src').rglob('*.rs'))
paths=sorted(set(paths));manifest={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
(root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(root/'evidence.tar.gz','w:gz') as t:
 for p in paths+[root/'manifest.json']:t.add(p,arcname=str(p.relative_to(root)))
print('Bundled',len(paths),'artifacts')
