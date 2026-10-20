from pathlib import Path
import hashlib,json,tarfile
a=Path(__file__).parent;ex=a.parent;r=ex/'breakthrough-local-de8-replay-20261020';r.mkdir(exist_ok=False);t=r/'candidate';t.mkdir();old=ex/'breakthrough-exact-witness-final-20261020';f=json.loads((old/'SOURCE-FREEZE.json').read_bytes());sha=lambda b:hashlib.sha256(b).hexdigest();expected=json.loads((old/'PUBLIC-SOURCE-VERIFICATION.json').read_bytes());assert expected['public_submission']=='de8bac6a-afff-479e-b716-8cbf2dce6c73'
for rel,h in f['protected_files'].items():
 data=(ex/'breakthrough-value-guard-fusion-audit-20261020/local-protected'/rel).read_bytes();assert sha(data)==h,rel;p=t/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
with tarfile.open(old/'point-add-source.tar.gz')as archive:
 members={m.name:m for m in archive.getmembers()};assert set(members)==set(f['source_files'])
 for rel,h in f['source_files'].items():
  p=Path(rel);assert not p.is_absolute()and'..'not in p.parts and rel.startswith('src/point_add/');m=members[rel];assert m.isfile();data=archive.extractfile(m).read();assert sha(data)==h,rel;p=t/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
freeze={'source_files':f['source_files'],'protected_files':f['protected_files'],'expected_stream_sha256':expected['exact_parent_stream_sha256'],'official_public_revision':expected['public_source_revision'],'official_submission':expected['public_submission'],'scope':'Unmodified local regeneration of current officialTde8, not a new candidate or benchmark. Require exact published source/stream before second-cache research.'};assert freeze['expected_stream_sha256']=='131712cc9c79e9ffd3ac60c07d097a29b5252c03afa95c891c5ecdd603c60c2e';(r/'SOURCE-FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\n');(r/'.gitignore').write_text('candidate/\n__pycache__/\n');(r/'.gitattributes').write_text('* -text\n')
(r/'verify.py').write_text('''import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'candidate';f=json.loads((r/'SOURCE-FREEZE.json').read_text());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());actual=sha(t/'ops.bin');assert actual==f['expected_stream_sha256'];(r/'RESULT.json').write_text(json.dumps({'status':'EXACT_CURRENT_OFFICIAL_DE8_SOURCE_AND_STREAM_REPRODUCED_LOCALLY','stream_sha256':actual,'source_files':len(f['source_files']),'protected_files':len(f['protected_files']),'scope':f['scope']},indent=2)+'\\n')
''')
base='/mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments';(r/'run-local.sh').write_bytes(('''#!/bin/sh
set -eu
cd BASE/breakthrough-local-de8-replay-20261020
export RUSTC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustc
export RUSTDOC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustdoc
export RUSTUP_AUTO_INSTALL=0
export CARGO_HOME=/root/.cargo
export CARGO_BUILD_JOBS=2
export OMP_NUM_THREADS=1
export CARGO_TARGET_DIR=BASE/breakthrough-value-guard-fusion-audit-20261020/local-tool/target
trap 's=$?; printf "%s\\n" "$s" > run.exit' EXIT
cd candidate
/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo build --release --locked --bin build_circuit > ../build.log 2>&1
timeout 1800 "$CARGO_TARGET_DIR/release/build_circuit" > ../generate.log 2>&1
cd ..
python3 verify.py
'''.replace('BASE',base)).encode());(r/'PLAN.md').write_text('''# Exact current officialT source before a second cache pass

Restore all205point_add and17protected bytes from verifiedde8/feba56de source.
Unchanged generation with existing localcompiler1.99 must produce exact official
stream131712cc; no new benchmark or score. Then fixed second-cache budgets0/16/
64 EXTRA wires may be tested, with existing9phase/guard/RNG/fault proof controls.
Extra width permitted for independentT objective. Any resource-improving source
needs fresh exact-prefix bindings/literal source/finalgate against exactde8,
qualified ascendingnonce/unchangedbenchmark before automatic challenge upload.
''');print(r.name)
