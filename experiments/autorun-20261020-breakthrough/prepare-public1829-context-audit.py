from pathlib import Path
import hashlib,json,shutil
a=Path(__file__).parent;ex=a.parent;old=ex/'breakthrough-public-best-drop-context-20261020/tool-source';r=ex/'breakthrough-public1829-context-audit-20261020';r.mkdir(exist_ok=False);t=r/'local-tool';t.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest()
for n in ['Cargo.lock','io.rs','discover.rs']:shutil.copyfile(old/n,t/n)
manifest=(old/'Cargo.toml').read_text().replace('/home/hclau/ecdsa_research/overnight-20261014/product-b3-baseline','../../breakthrough-value-guard-fusion-audit-20261020/local-protected');assert '/home/hclau/'not in manifest;(t/'Cargo.toml').write_text(manifest)
src=ex/'breakthrough-public1829-width-port-local-v4-20261020';f=json.loads((src/'SOURCE-FREEZE.json').read_bytes());res=json.loads((src/'RESULT.json').read_bytes());assert all(x['exit']==0 for x in res['cases']);inputs={x['mode']:x['stream_sha256']for x in res['cases']if x['mode']!='public'}
(r/'.gitignore').write_text('local-tool/\n__pycache__/\n*.ops.bin\n');(r/'.gitattributes').write_text('* -text\n');(r/'SOURCE-FREEZE.json').write_text(json.dumps({'tool_source_files':{n:sha((t/n).read_bytes())for n in ['Cargo.toml','Cargo.lock','io.rs','discover.rs']},'protected_files':f['protected_files'],'inputs':inputs,'input_constructor_source_freeze_sha256':sha((src/'SOURCE-FREEZE.json').read_bytes()),'extra_donors':0,'lookback':16384,'scope':'Fresh exact existing-wire context proofs on BOTH predeclared newpublic cap1234 andcap1233 whole streams. Nine inherited native phase/guard/reset/RNG/fault tests required. No old table transported; all source/input/record hashes bound. Component only, no finalgate, nonce or scored resources.'},indent=2)+'\n')
(r/'run.py').write_text('''import hashlib,json,os,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;f=json.loads((r/'SOURCE-FREEZE.json').read_text());src=r.parent/'breakthrough-public1829-width-port-local-v4-20261020';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert all(sha(r/'local-tool'/p)==h for p,h in f['tool_source_files'].items());deps=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-protected';assert all(sha(deps/p)==h for p,h in f['protected_files'].items());exe=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-tool/target/release/product_pareto_discover';stats=src/'stats-tool/target/release/native_width_stats';results={}
for mode,h in f['inputs'].items():
 path=src/mode/'ops.bin';assert sha(path)==h;start=time.monotonic()
 with(r/(mode+'.log')).open('xb')as log:subprocess.run(['timeout','1800',str(exe),str(path),str(r/mode)],env=dict(os.environ,RESEARCH_EXTRA_DONORS='0'),stdout=log,stderr=subprocess.STDOUT,check=True)
 with(r/(mode+'-stats.log')).open('xb')as log:subprocess.run([str(stats),str(r/(mode+'.ops.bin')),str(r/(mode+'-STATS.json'))],stdout=log,stderr=subprocess.STDOUT,check=True)
 proof=json.loads((r/(mode+'.json')).read_text());s=json.loads((r/(mode+'-STATS.json')).read_text());assert all(x[2]<proof['peak_qubits']for x in proof['leases']);assert s['qubits_protected_analyzer']<=proof['peak_qubits'];results[mode]={'leases':len(proof['leases']),'proposed':proof['proposed'],'qubits':s['qubits_protected_analyzer'],'diagnostic_weight':s['fair_guard_depth_proxy'],'diagnostic_saving':proof['depth_weight_saving_diagnostic'],'input_sha256':h,'output_sha256':sha(r/(mode+'.ops.bin')),'seconds':time.monotonic()-start};(r/'PROGRESS.json').write_text(json.dumps(results,indent=2)+'\\n')
assert all(sha(r/'local-tool'/p)==h for p,h in f['tool_source_files'].items());(r/'RESULT.json').write_text(json.dumps({'status':'FRESH_EXACT_CONTEXT_COMPONENT_COMPLETE_NOT_SCORED','native_controls':9,'cases':results,'scope':f['scope']},indent=2)+'\\n')
''')
base='/mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments';(r/'run-local.sh').write_bytes(('''#!/bin/sh
set -eu
cd BASE/breakthrough-public1829-context-audit-20261020
export RUSTC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustc
export RUSTDOC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustdoc
export RUSTUP_AUTO_INSTALL=0
export CARGO_HOME=/root/.cargo
export CARGO_BUILD_JOBS=2
export OMP_NUM_THREADS=1
export CARGO_TARGET_DIR=BASE/breakthrough-value-guard-fusion-audit-20261020/local-tool/target
trap 's=$?; printf "%s\\n" "$s" > run.exit' EXIT
/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo test --release --locked --manifest-path local-tool/Cargo.toml --bin product_pareto_discover -- --nocapture > tests.log 2>&1
grep -q 'test result: ok. 9 passed; 0 failed;' tests.log
/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo build --release --locked --manifest-path local-tool/Cargo.toml --bin product_pareto_discover > build.log 2>&1
python3 run.py
'''.replace('BASE',base)).encode());(r/'launch-local.sh').write_bytes(('''#!/bin/sh
set -eu
cd BASE/breakthrough-public1829-context-audit-20261020
test ! -e run.pid
nohup setsid sh run-local.sh > run.log 2>&1 < /dev/null &
printf '%s\\n' "$!" > run.pid
cat run.pid
'''.replace('BASE',base)).encode());(r/'PLAN.md').write_text('''# Fresh exact existing-wire caches for the completed newpublic width grid

Two fixed inputs: cap1234-t21 andcap1233-r012 from exact public1829 resource grid.
All9native comparator/plan/policy controls passed, publicstream bytecontrol exact.
Old public boundtables omitted in changed constructors. Reprove exactcontext
leases from scratch using zero EXTRA wires and16384lookback, same nine native
phase/guard/reset/RNG/fault controls as previously qualified proof engine. Freeze
source/input/protected hashes before discovery. Preserve ALL outcomes and both
resource cases; no point input/failure data is consulted. Component only; any
competitive source still needs literal construction/full bindings/fresh actual
development/OWN final gate/qualified ascendingnonce/full unchangedbenchmark/
local member review and authorized automatic challenge verification.
''');print(r.name)
