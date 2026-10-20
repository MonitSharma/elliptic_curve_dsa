"""Independent local test harness; exact LF-normalized official protected bytes."""
import hashlib,json,shutil
from pathlib import Path
root=Path(__file__).resolve().parents[2];ex=root/'experiments';r=ex/'breakthrough-value-guard-fusion-audit-20261020';src=ex/'breakthrough-zero-lifetime-audit-20261020';t=r/'local-tool';deps=r/'local-protected';t.mkdir(exist_ok=False);deps.mkdir(exist_ok=False)
sha=lambda b:hashlib.sha256(b).hexdigest();f=json.loads((src/'SOURCE-FREEZE.json').read_bytes());prefix='/home/hclau/ecdsa_research/overnight-20261014/product-b3-baseline/'
protected={}
for name,h in f['protected_dependency_files'].items():
 assert name.startswith(prefix);rel=name[len(prefix):];data=(root/'agents/toffoli'/rel).read_bytes().replace(b'\r\n',b'\n');assert sha(data)==h,rel
 p=deps/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);protected[rel]=h
for name in ['Cargo.lock','io.rs']:shutil.copyfile(src/'tool-source'/name,t/name)
shutil.copyfile(r/'audit.rs',t/'audit.rs')
manifest=(src/'tool-source/Cargo.toml').read_text().replace('/home/hclau/ecdsa_research/overnight-20261014/product-b3-baseline','../local-protected').replace('zero_lifetime_audit','value_ir_audit');(t/'Cargo.toml').write_text(manifest)
(r/'LOCAL-TEST-FREEZE.json').write_text(json.dumps({'status':'LOCAL_VERIFICATION_TOOL_SOURCE_FROZEN_BEFORE_NATIVE_TESTS','protected_files':protected,'source_files':{n:sha((t/n).read_bytes())for n in ['Cargo.toml','Cargo.lock','io.rs','audit.rs']},'scope':'All17 protected files restored to exact server-frozen LF bytes in a separate read-only dependency copy. Only verification tool Cargo path differs. Existing local compiler1.99; server1.93 controls still required. No candidate/nonce/gate/score.'},indent=2)+'\n')
p=r/'.gitignore';s=p.read_text();p.write_text(s+'local-tool/\nlocal-protected/\n')
(r/'run-local-tests.sh').write_text('''#!/bin/sh
set -eu
cd /mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments/breakthrough-value-guard-fusion-audit-20261020/local-tool
export RUSTC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustc
export RUSTDOC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustdoc
export RUSTUP_AUTO_INSTALL=0
export CARGO_HOME=/root/.cargo
export CARGO_BUILD_JOBS=2
export OMP_NUM_THREADS=1
set +e
/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo test --offline --release --locked --bin value_ir_audit -- --nocapture > ../local-native.log 2>&1
status=$?
set -e
printf '%s\\n' "$status" > ../local-native.exit
exit "$status"
''')
print('Local tool and17 exact protected dependency files frozen')
