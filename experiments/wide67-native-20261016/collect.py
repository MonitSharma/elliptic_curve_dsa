from pathlib import Path
import hashlib,json,tarfile
root=Path(__file__).resolve().parent
allowed={'.py','.rs','.c','.h','.sh','.md','.json','.jsonl','.log','.err','.out','.sha256','.csv','.tsv','.exit','.pid','.txt','.in','.patch'}
paths=[]
for p in root.rglob('*'):
 if not p.is_file() or any(x in p.relative_to(root).parts for x in ['candidate','target','.git']):continue
 if p.name in ['manifest.json','verified-manifest.json']:continue
 if p.suffix in allowed or p.name=='point-add-source.tar.gz':paths.append(p)
paths=sorted(set(paths));manifest={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
(root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(root/'evidence.tar.gz','w:gz') as out:
 for p in paths+[root/'manifest.json']:out.add(p,arcname=str(p.relative_to(root)))
print('Archived',len(paths),'artifacts including full binary submission source; large ops remain server-side')
