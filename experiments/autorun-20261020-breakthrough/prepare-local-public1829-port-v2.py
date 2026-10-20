"""Portable local counterpart of the declared new-public resource grid."""
from pathlib import Path
import ast,hashlib,json,shutil,tarfile
root=Path(__file__).resolve().parents[2];ex=root/'experiments';a=Path(__file__).parent;old=ex/'breakthrough-public1829-width-port-20261020';r=ex/'breakthrough-public1829-width-port-local-v2-20261020';r.mkdir(exist_ok=False);t=r/'observer';t.mkdir();parent=ex/'breakthrough-public1829-reproduction-20261020';f=json.loads((parent/'SOURCE-FREEZE.json').read_bytes());sha=lambda b:hashlib.sha256(b).hexdigest()
for rel,h in f['protected_files'].items():
 data=(ex/'breakthrough-value-guard-fusion-audit-20261020/local-protected'/rel).read_bytes();assert sha(data)==h,rel;p=t/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
with tarfile.open(parent/'point-add-source.tar.gz')as archive:
 files={m.name:m for m in archive.getmembers()};assert set(files)==set(f['source_files'])
 for rel,h in f['source_files'].items():
  name=Path(rel);assert not name.is_absolute()and'..'not in name.parts and rel.startswith('src/point_add/');m=files[rel];assert m.isfile();data=archive.extractfile(m).read();assert sha(data)==h,rel;p=t/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
for n in ['.gitattributes','.gitignore','additional-tests.rs','phase-compare-compact.rs','drop-policy-tests.rs']:shutil.copyfile(old/n,r/n)
s=(old/'prepare.py').read_text();start=s.index("r=Path(__file__)");end=s.index("p=t/'src/point_add/mod.rs'",start)
s=s[:start]+'''r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';base='3eefcf216ca37cba0ae3f56212d6b1302844a249';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();parent=ws/'breakthrough-public1829-reproduction-20261020';f=json.loads((parent/'SOURCE-FREEZE.json').read_text());parent_result=json.loads((parent/'RESULT.json').read_text());assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());protected=f['protected_files']
''' +s[end:]
start=s.index("reference=r.parent/'breakthrough-native-both-final");end=s.index("raw+=b'\\n'+tests",start)
s=s[:start]+"tests=(ws/'breakthrough-public-drop-tradeoffs-v2-20261020/ported-native-tests.rs').read_bytes();"+s[end:]
start=s.index("prior=parent/'parent/target'");end=s.index("(r/'SOURCE-FREEZE.json')",start)
s=s[:start]+'''import difflib,tarfile
original={}
with tarfile.open(parent/'point-add-source.tar.gz')as archive:
 for m in archive.getmembers():original[m.name]=archive.extractfile(m).read()
patch=[]
for p in sorted((t/'src/point_add').rglob('*')):
 if p.is_file():
  rel=p.relative_to(t).as_posix();before=original.get(rel,b'');after=p.read_bytes()
  if before!=after:patch.extend(difflib.unified_diff(before.decode().splitlines(True),after.decode().splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
(r/'source.patch').write_text(''.join(patch));''' +s[end:]
ast.parse(s);(r/'prepare.py').write_text(s)
stats=r/'stats-tool';stats.mkdir();oldstats=ex/'breakthrough-stackv3-width-stats-20261020/tool-source'
for n in ['Cargo.lock','io.rs','stats.rs']:shutil.copyfile(oldstats/n,stats/n)
s=(oldstats/'Cargo.toml').read_text();import re
s=s.replace('/home/hclau/ecdsa_research/overnight-20261014/product-b3-baseline','../observer');assert '/home/hclau/'not in s;(stats/'Cargo.toml').write_text(s)
s=(old/'run.py').read_text().replace("'/home/hclau/.cargo/bin/cargo','+1.93.0'","'/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo'")
s=s.replace("r.parent/'breakthrough-stackv3-width-stats-20261020/tool/target/release/native_width_stats'","r/'stats-tool/target/release/native_width_stats'")
ast.parse(s);(r/'run.py').write_text(s)
shutil.copyfile(old/'PLAN.md',r/'PLAN.md');(r/'LOCAL-PROVENANCE.json').write_text(json.dumps({'status':'LOCAL_PORTABLE_RESEARCH_GRID_PREPARED_NOT_LAUNCHED','server_grid_plan':'breakthrough-public1829-width-port-20261020','public_parent_source_files_verified':len(f['source_files']),'protected_files_verified':len(f['protected_files']),'compiler':'Existing local Rust1.99, exact public stream bytecontrol required; not an official score','native_plan_tests':'Previously archived exact plan7 test bytes, no source comparator harness changes','old_source_or_gate_reused':False},indent=2)+'\n')
p=r/'.gitignore';p.write_text(p.read_text()+'stats-tool/target/\n')
base='/mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments';script='''#!/bin/sh
set -eu
cd BASE/breakthrough-public1829-width-port-local-v2-20261020
export RUSTC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustc
export RUSTDOC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustdoc
export RUSTUP_AUTO_INSTALL=0
export CARGO_HOME=/root/.cargo
export CARGO_BUILD_JOBS=2
export OMP_NUM_THREADS=1
trap 's=$?; printf "%s\\n" "$s" > local-controller.exit' EXIT
/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo build --release --locked --manifest-path stats-tool/Cargo.toml --bin native_width_stats > stats-build.log 2>&1
python3 run.py
'''.replace('BASE',base);(r/'run-local.sh').write_bytes(script.encode())
(r/'launch-local.sh').write_bytes(('''#!/bin/sh
set -eu
cd BASE/breakthrough-public1829-width-port-local-v2-20261020
test ! -e local-controller.pid
nohup setsid sh run-local.sh > local-controller.log 2>&1 < /dev/null &
printf '%s\\n' "$!" > local-controller.pid
cat local-controller.pid
'''.replace('BASE',base)).encode())
print(r.name,'source verified, source patch prepared at launch')
