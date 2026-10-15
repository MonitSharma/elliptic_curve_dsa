from pathlib import Path
import hashlib,json,tarfile
root=Path('/home/hclau/ecdsa_research/precision-family-20261016')
skip={'evidence.tar.gz','evidence.sha256','manifest.json','verified-manifest.json'}
paths=[];external={}
for p in root.iterdir():
 if not p.is_file() or p.name in skip:continue
 if p.stat().st_size>30_000_000:
  external[str(p)]=dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),status='preserved server-only; not an archive member')
 else:paths.append(p)
for folder in ['isolated','fresh-paired']:
 for p in(root/folder).rglob('*'):
  if not p.is_file():continue
  if p.name=='raw-builder.bin':
   external[str(p)]=dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),status='preserved server-only; not an archive member')
  else:paths.append(p)
for p in[root/'candidate/ops.bin',root.parent/'product-exact-20261015/tip/ops.bin']:
 external[str(p)]=dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),status='preserved server-only; not an archive member')
files={str(p.relative_to(root)):dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())for p in paths}
m=root/'manifest.json';m.write_text(json.dumps(dict(files=files,external=external),indent=2)+'\n');paths.append(m)
archive=root/'evidence.tar.gz'
with tarfile.open(archive,'w:gz')as t:
 for p in sorted(paths):t.add(p,arcname=str(p.relative_to(root)),recursive=False)
h=hashlib.sha256(archive.read_bytes()).hexdigest();(root/'evidence.sha256').write_text(h+'  evidence.tar.gz\n');print(h,len(files),len(external),archive.stat().st_size)
