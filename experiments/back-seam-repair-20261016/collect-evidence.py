from pathlib import Path
import hashlib,json,tarfile
r=Path('/home/hclau/ecdsa_research/back-seam-repair-20261016')
assert (r/'fresh-paired.exit').read_text().strip()=='0'
assert (r/'phase-proofs.exit').read_text().strip()=='0'
assert (r/'native-verification.exit').read_text().strip()=='0'
skip={'evidence.tar.gz','evidence.sha256','manifest.json','verified-manifest.json'}
paths=set();external={}
def add(p,force=False):
 if not p.is_file() or p.name in skip:return
 if not force and (p.stat().st_size>25_000_000 and p.suffix!='.log' or p.name.startswith('preserved-')):
  external[str(p)]=dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),status='preserved server-only; not an archive member')
 else:paths.add(p)
for p in r.iterdir():add(p)
for p in (r/'fresh-paired').rglob('*'):add(p,True)
for folder in ['candidate','tool','observer']:
 for p in (r/folder/'src').rglob('*'):add(p,True)
 for n in ['Cargo.toml','Cargo.lock','rust-toolchain.toml']:
  add(r/folder/n,True)
add(r/'candidate/ops.bin')
p=r.parent/'product-exact-20261015/tip/ops.bin'
external[str(p)]=dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),status='preserved original server-only stream; not an archive member')
files={str(p.relative_to(r)):dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())for p in sorted(paths)}
m=r/'manifest.json';m.write_text(json.dumps(dict(files=files,external=external),indent=2)+'\n');paths.add(m)
with tarfile.open(r/'evidence.tar.gz','w:gz')as t:
 for p in sorted(paths):t.add(p,arcname=str(p.relative_to(r)),recursive=False)
h=hashlib.sha256((r/'evidence.tar.gz').read_bytes()).hexdigest();(r/'evidence.sha256').write_text(h+'  evidence.tar.gz\n')
print(h,len(files),len(external),(r/'evidence.tar.gz').stat().st_size)
