from pathlib import Path
import hashlib,json,sys,tarfile
root=Path(sys.argv[1] if len(sys.argv)>1 else Path(__file__).resolve().parent).resolve()
allowed={'.py','.rs','.c','.h','.sh','.md','.json','.jsonl','.log','.err','.out','.sha256','.csv','.tsv','.exit','.pid','.txt','.in'}
paths=[]
for p in root.rglob('*'):
 if not p.is_file() or 'target' in p.relative_to(root).parts or '.git' in p.relative_to(root).parts:continue
 if p.name in ['manifest.json','verified-manifest.json']:continue
 if p.suffix in allowed or p.name in ['Cargo.toml','Cargo.lock']:paths.append(p)
paths=sorted(set(paths));manifest={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
(root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(root/'evidence.tar.gz','w:gz') as archive:
 for p in paths+[root/'manifest.json']:archive.add(p,arcname=str(p.relative_to(root)))
print(root.name,'bundled',len(paths),'artifacts')
