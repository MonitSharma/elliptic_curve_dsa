from pathlib import Path
import hashlib,json,shutil
a=Path(__file__).parent;ex=a.parent;r=ex/'breakthrough-public1829-lifetime-audit-20261020';r.mkdir(exist_ok=False);t=r/'local-tool';t.mkdir();old=ex/'breakthrough-zero-lifetime-audit-20261020/tool-source';sha=lambda b:hashlib.sha256(b).hexdigest()
for n in ['Cargo.lock','io.rs','audit.rs']:shutil.copyfile(old/n,t/n)
manifest=(old/'Cargo.toml').read_text().replace('/home/hclau/ecdsa_research/overnight-20261014/product-b3-baseline','../../breakthrough-value-guard-fusion-audit-20261020/local-protected');(t/'Cargo.toml').write_text(manifest);shutil.copyfile(t/'audit.rs',r/'audit.rs');(r/'.gitignore').write_text('local-tool/\n__pycache__/\n');(r/'.gitattributes').write_text('* -text\n');f=json.loads((ex/'breakthrough-public1829-width-port-local-v4-20261020/SOURCE-FREEZE.json').read_bytes());result=json.loads((ex/'breakthrough-public1829-width-port-local-v4-20261020/RESULT.json').read_bytes());assert all(x['exit']==0 for x in result['cases']);(r/'SOURCE-FREEZE.json').write_text(json.dumps({'source_files':{n:sha((t/n).read_bytes())for n in ['Cargo.toml','Cargo.lock','io.rs','audit.rs']},'protected_files':f['protected_files'],'inputs':{x['mode']:x['stream_sha256']for x in result['cases']},'scope':'Read-only lifetime/color audit on exact newpublic1829 stream and completed exactworkspace grid. No new candidate, emitted stream, nonce, gate or scored resource. Provisional colors only; independent native phase/value/RNG proof mandatory before any rewrite.'},indent=2)+'\n')
(r/'run.py').write_text('''import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;f=json.loads((r/'SOURCE-FREEZE.json').read_text());src=r.parent/'breakthrough-public1829-width-port-local-v4-20261020';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert all(sha(r/'local-tool'/p)==h for p,h in f['source_files'].items());deps=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-protected';assert all(sha(deps/p)==h for p,h in f['protected_files'].items());exe=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-tool/target/release/zero_lifetime_audit';results={}
for mode,h in f['inputs'].items():
 p=src/mode/'ops.bin';assert sha(p)==h
 with(r/(mode+'.log')).open('xb')as log:subprocess.run([str(exe),str(p),str(r/(mode+'.json'))],stdout=log,stderr=subprocess.STDOUT,check=True)
 results[mode]=json.loads((r/(mode+'.json')).read_text())
(r/'RESULT.json').write_text(json.dumps({'status':'READ_ONLY_PROVISIONAL_PUBLIC1829_LIFETIME_AUDIT_NOT_A_RESOURCE_RECORD','cases':results,'scope':f['scope'],'binary_sha256':sha(exe)},indent=2)+'\\n')
''')
base='/mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments';(r/'run-local.sh').write_bytes(('''#!/bin/sh
set -eu
cd BASE/breakthrough-public1829-lifetime-audit-20261020
export RUSTC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustc
export RUSTDOC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustdoc
export RUSTUP_AUTO_INSTALL=0
export CARGO_HOME=/root/.cargo
export CARGO_BUILD_JOBS=2
export OMP_NUM_THREADS=1
export CARGO_TARGET_DIR=BASE/breakthrough-value-guard-fusion-audit-20261020/local-tool/target
trap 's=$?; printf "%s\\n" "$s" > run.exit' EXIT
/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo build --release --locked --manifest-path local-tool/Cargo.toml --bin zero_lifetime_audit > build.log 2>&1
python3 run.py
'''.replace('BASE',base)).encode());(r/'launch-local.sh').write_bytes(('''#!/bin/sh
set -eu
cd BASE/breakthrough-public1829-lifetime-audit-20261020
test ! -e run.pid
nohup setsid sh run-local.sh > run.log 2>&1 < /dev/null &
printf '%s\\n' "$!" > run.pid
cat run.pid
'''.replace('BASE',base)).encode());(r/'PLAN.md').write_text('''# Read-only fresh public-product lifetime/color audit

Prior lifetime audit was on strong wideT71, not newproduct1829. Check whether
public source-bound postpasses freed temporary lifetimes at the actual peak.
Use unchanged conservative lexical reset-dominance tool on all three completed
newpublic workspace streams. No emitted candidate or resource record; widths
are provisional colors only. Any later physicalwire rewrite requires independent
phase/value/guard/RNG/fault controls, frozen source and own finalgate/nonce/full
unchangedbenchmark before automatic challenge verification. Registered inputs
pinned, classical bits/conditions/RNG draws unchanged in this diagnostic.
''');print(r.name)
