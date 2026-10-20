"""Rebuild frozen research stream locally, requiring exact hash before filter audit."""
import hashlib,json,shutil,tarfile
from pathlib import Path
root=Path(__file__).resolve().parents[2];ex=root/'experiments';r=ex/'breakthrough-local-product-filter-replay-20261020';r.mkdir(exist_ok=False);t=r/'candidate';t.mkdir();src=ex/'breakthrough-public-best-drop-finished-20261020';audit=ex/'breakthrough-value-guard-fusion-audit-20261020';f=json.loads((src/'SOURCE-FREEZE.json').read_bytes());sha=lambda b:hashlib.sha256(b).hexdigest()
assert (audit/'local-native-online.exit').read_text().strip()=='0';assert 'test result: ok. 20 passed; 0 failed;'in(audit/'local-native-online.log').read_text()
for rel,h in f['protected_files'].items():
 data=(audit/'local-protected'/rel).read_bytes();assert sha(data)==h,rel;p=t/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
with tarfile.open(src/'preserved-point-add-source.tar.gz')as archive:
 files={m.name:m for m in archive.getmembers()};assert set(files)==set(f['source_files'])
 for rel,h in f['source_files'].items():
  p=Path(rel);assert not p.is_absolute()and'..'not in p.parts and rel.startswith('src/point_add/');m=files[rel];assert m.isfile();data=archive.extractfile(m).read();assert sha(data)==h,rel;p=t/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
(r/'.gitignore').write_text('candidate/\n__pycache__/\n*.ops.bin\n');(r/'.gitattributes').write_text('* -text\n')
config={'status':'FROZEN_OLD_PRODUCT_RESEARCH_REPLAY_NOT_A_NEW_CANDIDATE_OR_SCORE','source_files':f['source_files'],'protected_files':f['protected_files'],'expected_ops_sha256':'6192778816154b713a714446b3e7d28165a649460173a3e3f17d9de06fa7bb96','compiler':'Existing local Rust1.99, crosscompiler byte-for-byte stream hash required before audit','local_guard_fusion_native_tests':20,'scope':'Old superseded candidate/gate remain final; no nonce/benchmark/submission. Reproduction only to unblock independent verification filter research while server inaccessible.'};(r/'SOURCE-FREEZE.json').write_text(json.dumps(config,indent=2)+'\n')
base='/mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments';script='''#!/bin/sh
set -eu
cd BASE/breakthrough-local-product-filter-replay-20261020
export RUSTC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustc
export RUSTDOC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustdoc
export RUSTUP_AUTO_INSTALL=0
export CARGO_HOME=/root/.cargo
export CARGO_BUILD_JOBS=2
export OMP_NUM_THREADS=1
export CARGO_TARGET_DIR=BASE/breakthrough-value-guard-fusion-audit-20261020/local-tool/target
trap 's=$?; printf "%s\\n" "$s" > run.exit' EXIT
cd candidate
set +e
/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo build --release --locked --bin build_circuit > ../build.log 2>&1
s=$?
printf '%s\\n' "$s" > ../build.exit
set -e
test "$s" = 0
timeout 1800 "$CARGO_TARGET_DIR/release/build_circuit" > ../generate.log 2>&1
cd ..
python3 verify-and-audit.py
'''.replace('BASE',base)
(r/'run-local.sh').write_bytes(script.encode())
(r/'verify-and-audit.py').write_text('''import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'candidate';f=json.loads((r/'SOURCE-FREEZE.json').read_text());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
assert all(sha(t/p)==h for p,h in {**f['source_files'],**f['protected_files']}.items())
actual=sha(t/'ops.bin');assert actual==f['expected_ops_sha256'],actual
(r/'STREAM-REPRODUCTION.json').write_text(json.dumps({'status':'EXACT_OLD_FROZEN_STREAM_REPRODUCED_WITH_LOCAL_COMPILER','stream_sha256':actual,'source_files':len(f['source_files']),'protected_files':len(f['protected_files']),'scope':f['scope']},indent=2)+'\\n')
audit=r.parent/'breakthrough-value-guard-fusion-audit-20261020';tool=audit/'local-tool';compiler='/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo'
with (r/'audit-build.log').open('xb')as log:subprocess.run([compiler,'build','--release','--locked','--bin','value_ir_audit'],cwd=tool,stdout=log,stderr=subprocess.STDOUT,check=True)
with (r/'full-audit.log').open('xb')as log:subprocess.run([str(tool/'target/release/value_ir_audit'),str(t/'ops.bin'),str(r/'full-audit.json')],stdout=log,stderr=subprocess.STDOUT,check=True)
result=json.loads((r/'full-audit.json').read_text());(r/'RESULT.json').write_text(json.dumps({'status':'EXACT_LOCAL_STREAM_REPLAY_AND_VERIFICATION_ONLY_AUDIT_COMPLETE','native_controls':20,'audit':result,'scope':f['scope']},indent=2)+'\\n')
''')
(r/'launch-local.sh').write_bytes(('''#!/bin/sh
set -eu
cd BASE/breakthrough-local-product-filter-replay-20261020
test ! -e run.pid
nohup setsid sh run-local.sh > run.log 2>&1 < /dev/null &
printf '%s\\n' "$!" > run.pid
cat run.pid
'''.replace('BASE',base)).encode())
print(r.name,len(f['source_files']),'frozen source files;17 protected')
