from pathlib import Path
import hashlib,json,tarfile
r=Path('/home/hclau/ecdsa_research/phase-localization-20261016');paths=[];external={};skip={'evidence.tar.gz','evidence.sha256','manifest.json','verified-manifest.json'}
for p in r.iterdir():
 if not p.is_file()or p.name in skip:continue
 if p.name in['compact.bin','raw-builder.bin']or p.stat().st_size>20_000_000 and not p.name.endswith('.log'):
  external[str(p)]=dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),status='preserved server-only; not an archive member')
 else:paths.append(p)
for folder in['tool','source-observer','source-observer-v2']:
 for p in(r/folder/'src').rglob('*.rs'):paths.append(p)
 for name in['Cargo.toml','Cargo.lock','rust-toolchain.toml']:
  p=r/folder/name
  if p.exists():paths.append(p)
p=r.parent/'product-exact-20261015/tip/ops.bin';external[str(p)]=dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),status='preserved server-only original frozen stream; not an archive member')
files={str(p.relative_to(r)):dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())for p in paths};m=r/'manifest.json';m.write_text(json.dumps(dict(files=files,external=external),indent=2)+'\n');paths.append(m)
with tarfile.open(r/'evidence.tar.gz','w:gz')as t:
 for p in sorted(paths):t.add(p,arcname=str(p.relative_to(r)),recursive=False)
h=hashlib.sha256((r/'evidence.tar.gz').read_bytes()).hexdigest();(r/'evidence.sha256').write_text(h+'  evidence.tar.gz\n');print(h,len(files),len(external),(r/'evidence.tar.gz').stat().st_size)
