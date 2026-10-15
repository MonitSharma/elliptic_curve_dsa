from pathlib import Path
import hashlib,json,tarfile,shutil
r=Path('/home/hclau/ecdsa_research/value-carry-contracts-20261016')
for name in ['square-fresh.exit','square-paired-summary.exit','square-native-verification.exit','protected-dirty-square.exit','whole-square.exit','support.exit','terminal-analysis.exit','square-analysis.exit']:
 assert(r/name).read_text().strip()=='0',name
base=r.parent/'product-exact-20261015/tip';ref=r/'source-reference';ref.mkdir(exist_ok=True)
for name in ['src/circuit.rs','src/sim.rs','src/bin/build_circuit.rs','src/bin/eval_circuit.rs','Cargo.toml','Cargo.lock']:
 dst=ref/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(base/name,dst)
skip={'evidence.tar.gz','evidence.sha256','manifest.json','verified-manifest.json'};paths=set();external={}
def add(p,force=False):
 if not p.is_file()or p.name in skip:return
 if not force and(p.name.startswith('preserved-')or p.stat().st_size>25_000_000 and p.suffix not in['.log','.json','.jsonl']):
  external[str(p)]=dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),status='preserved server-only; not an archive member')
 else:paths.add(p)
for p in r.iterdir():add(p)
for folder in ['square-fresh','square-component','source-reference']:
 for p in(r/folder).rglob('*'):add(p)
for folder in ['square4-candidate','observer','square-observer','tool']:
 for p in(r/folder/'src').rglob('*'):add(p,True)
 for name in ['Cargo.toml','Cargo.lock','rust-toolchain.toml']:add(r/folder/name,True)
add(r/'square4-candidate/ops.bin')
for p in [base/'ops.bin',r.parent/'precision-repair-20261016/surviving-folds.json',r.parent/'prefilter-20261015/a29-edited-folds-v1/original-candidates.json',r.parent/'precision-family-20261016/constant_zero.so']:
 external[str(p)]=dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),status='preserved external dependency; not an archive member')
files={str(p.relative_to(r)):dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())for p in sorted(paths)}
m=r/'manifest.json';m.write_text(json.dumps(dict(files=files,external=external),indent=2)+'\n');paths.add(m)
with tarfile.open(r/'evidence.tar.gz','w:gz')as t:
 for p in sorted(paths):t.add(p,arcname=str(p.relative_to(r)),recursive=False)
h=hashlib.sha256((r/'evidence.tar.gz').read_bytes()).hexdigest();(r/'evidence.sha256').write_text(h+'  evidence.tar.gz\n');print(h,len(files),len(external),(r/'evidence.tar.gz').stat().st_size)
