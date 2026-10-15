from pathlib import Path
import hashlib,json,tarfile
r=Path('/home/hclau/ecdsa_research/free-borrow-family-20261016');paths=set();external={};skip={'evidence.tar.gz','evidence.sha256','manifest.json','verified-manifest.json'}
assert(r/'raw-verification.exit').read_text().strip()=='0'and(r/'audit-affine.exit').read_text().strip()=='0'
for p in r.iterdir():
 if not p.is_file()or p.name in skip:continue
 if p.name in['raw-builder.bin','preserved-source-v2-build_circuit']:
  external[str(p)]=dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),status='preserved server-only; not an archive member')
 else:paths.add(p)
for p in(r/'observer/src').rglob('*'):
 if p.is_file():paths.add(p)
for n in['Cargo.toml','Cargo.lock','rust-toolchain.toml']:
 p=r/'observer'/n
 if p.exists():paths.add(p)
files={str(p.relative_to(r)):dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())for p in sorted(paths)}
m=r/'manifest.json';m.write_text(json.dumps(dict(files=files,external=external),indent=2)+'\n');paths.add(m)
with tarfile.open(r/'evidence.tar.gz','w:gz')as t:
 for p in sorted(paths):t.add(p,arcname=str(p.relative_to(r)),recursive=False)
h=hashlib.sha256((r/'evidence.tar.gz').read_bytes()).hexdigest();(r/'evidence.sha256').write_text(h+'  evidence.tar.gz\n');print(h,len(files),len(external),(r/'evidence.tar.gz').stat().st_size)
