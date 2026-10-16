from pathlib import Path
import hashlib,json,tarfile,io
root=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if(root/'evidence.tar.gz').exists()and not(root/'receipt.json').exists():
 fail=root/'initial-path-format-failure';fail.mkdir(exist_ok=False)
 for name in ['evidence.tar.gz','manifest.json']:(root/name).rename(fail/name)
 (fail/'NOTE.txt').write_text('Initial local archive verification failed because Windows manifest keys used backslashes while tar members normalized to forward slashes. Source/results unchanged; corrected collector uses as_posix paths.\n')
files=[p for p in root.rglob('*')if p.is_file()and p.relative_to(root).as_posix()not in['evidence.tar.gz','receipt.json','manifest.json']]
manifest={p.relative_to(root).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size}for p in files};raw=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode();(root/'manifest.json').write_bytes(raw)
with tarfile.open(root/'evidence.tar.gz','w:gz')as t:
 for p in files:t.add(p,arcname=p.relative_to(root).as_posix(),recursive=False)
 info=tarfile.TarInfo('manifest.json');info.size=len(raw);t.addfile(info,io.BytesIO(raw))
with tarfile.open(root/'evidence.tar.gz','r:gz')as t:
 for name,item in manifest.items():assert hashlib.sha256(t.extractfile(name).read()).hexdigest()==item['sha256']
receipt={'status':'ALL_RENDERER_SOURCE_ARTIFACTS_VERIFIED','members':len(files),'archive_sha256':sha(root/'evidence.tar.gz'),'archive_bytes':(root/'evidence.tar.gz').stat().st_size};(root/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
