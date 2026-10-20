from pathlib import Path
import hashlib,json,shutil
a=Path(__file__).parent;ex=a.parent;r=ex/'breakthrough-de8-second-cache-20261020';r.mkdir(exist_ok=False);t=r/'local-tool';t.mkdir();old=ex/'breakthrough-public1829-context-audit-20261020/local-tool';sha=lambda b:hashlib.sha256(b).hexdigest()
for n in ['Cargo.toml','Cargo.lock','io.rs','discover.rs']:shutil.copyfile(old/n,t/n)
replay=ex/'breakthrough-local-de8-replay-20261020';assert(replay/'run.exit').read_text().strip()=='0';f=json.loads((replay/'SOURCE-FREEZE.json').read_bytes());assert sha((replay/'candidate/ops.bin').read_bytes())==f['expected_stream_sha256'];(r/'SOURCE-FREEZE.json').write_text(json.dumps({'tool_source_files':{n:sha((t/n).read_bytes())for n in ['Cargo.toml','Cargo.lock','io.rs','discover.rs']},'protected_files':f['protected_files'],'input_stream_sha256':f['expected_stream_sha256'],'input_constructor_source_freeze_sha256':sha((replay/'SOURCE-FREEZE.json').read_bytes()),'declared_extra_donor_budgets':[0,16,64],'lookback':16384,'native_controls':9,'scope':'Fixed second exact context-cache pass on complete currentofficialde8 stream, all205source/17protected bytes andframe reproduced. Extra width allowed for independentT objective. Reprove every lease from scratch, no old table or statistical verdict reused. Component only, no score/gate/nonce.'},indent=2)+'\n');(r/'.gitignore').write_text('local-tool/\n__pycache__/\n*.ops.bin\n');(r/'.gitattributes').write_text('* -text\n')
(r/'run.py').write_text('''import hashlib,json,os,resource,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;f=json.loads((r/'SOURCE-FREEZE.json').read_text());src=r.parent/'breakthrough-local-de8-replay-20261020';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert all(sha(r/'local-tool'/p)==h for p,h in f['tool_source_files'].items());assert sha(src/'candidate/ops.bin')==f['input_stream_sha256'];deps=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-protected';assert all(sha(deps/p)==h for p,h in f['protected_files'].items());exe=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-tool/target/release/product_pareto_discover';stats=r.parent/'breakthrough-public1829-width-port-local-v4-20261020/stats-tool/target/release/native_width_stats';results={}
def limits():resource.setrlimit(resource.RLIMIT_AS,(5*1024**3,5*1024**3));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
for extra in f['declared_extra_donor_budgets']:
 name='extra'+str(extra);start=time.monotonic()
 with(r/(name+'.log')).open('xb')as log:
  p=subprocess.Popen(['timeout','1200',str(exe),str(src/'candidate/ops.bin'),str(r/name)],env=dict(os.environ,RESEARCH_EXTRA_DONORS=str(extra)),stdout=log,stderr=subprocess.STDOUT,preexec_fn=limits);(r/(name+'.pid')).write_text(str(p.pid)+'\\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\\n');row={'exit':rc,'seconds':time.monotonic()-start}
 if rc==0:
  proof=json.loads((r/(name+'.json')).read_text());assert all(x[2]<1464+extra for x in proof['leases'])
  with(r/(name+'-stats.log')).open('xb')as log:subprocess.run([str(stats),str(r/(name+'.ops.bin')),str(r/(name+'-STATS.json'))],stdout=log,stderr=subprocess.STDOUT,check=True)
  s=json.loads((r/(name+'-STATS.json')).read_text());assert s['qubits_protected_analyzer']<=1464+extra;row.update(leases=len(proof['leases']),proposed=proof['proposed'],diagnostic_saving=proof['depth_weight_saving_diagnostic'],output_sha256=sha(r/(name+'.ops.bin')),static_diagnostics=s)
 results[name]=row;(r/'PROGRESS.json').write_text(json.dumps(results,indent=2)+'\\n')
(r/'RESULT.json').write_text(json.dumps({'status':'FIXED_SECOND_CACHE_RESOURCE_GRID_COMPLETE_NOT_SCORED','native_controls':9,'cases':results,'scope':f['scope']},indent=2)+'\\n')
''')
base='/mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments';(r/'run-local.sh').write_bytes(('''#!/bin/sh
set -eu
cd BASE/breakthrough-de8-second-cache-20261020
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
'''.replace('BASE',base)).encode());(r/'PLAN.md').write_text('''# Fixed second-cache grid on current official T746114

Exactcurrentde8 stream131712 reconstructedfromall205source/17protected bytes.
Fixed extra donor budgets0/16/64, all declared BEFORE fresh point inputs. Same
native9phase/guard/reset/RNG/fault proof engine; every candidate lease freshly
proved against this complete input. Width free for independentT goal. Preserve
all outputs and resource failures. Any selected gain needs literal finished
source/fresh prefix bindings/native/development/OWN finalgate vs exactde8/
qualified ascendingnonce/unchangedbenchmark/localreview/automaticchallengeupload.
Static proxy/native counts never scored or added to README resultplots.
''');print(r.name)
