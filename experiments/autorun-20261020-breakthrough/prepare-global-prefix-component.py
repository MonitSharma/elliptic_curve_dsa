from pathlib import Path
import hashlib,json,shutil
a=Path(__file__).parent;ex=a.parent;old=ex/'breakthrough-public1829-context-audit-20261020/local-tool';r=ex/'breakthrough-global-prefix-component-20261020';r.mkdir(exist_ok=False);t=r/'local-tool';t.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest()
for n in ['Cargo.lock','io.rs']:shutil.copyfile(old/n,t/n)
s=(old/'discover.rs').read_text().replace('fn main(){','fn legacy_main(){',1);s+='\n'+(a/'global-prefix-simplify.rs').read_text()+'''
fn main(){let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),3);let ops=io::load_ops(&args[1]);let(out,stats)=global_prefix_simplify(&ops,1024);let result=serde_json::json!({"status":"GLOBAL_FULL_PREFIX_COMPONENT_PROOFS_COMPLETE_NOT_SCORED","input_records_sha3":hash(&ops),"output_records_sha3":hash(&out),"input_count":ops.len(),"output_count":out.len(),"proof":stats});std::fs::write(format!("{}.json",args[2]),serde_json::to_string_pretty(&result).unwrap()+"\\n").unwrap();io::save_ops(&format!("{}.ops.bin",args[2]),&out);println!("{result}");}
''';(t/'discover.rs').write_text(s);(r/'global-prefix-simplify.rs').write_text((a/'global-prefix-simplify.rs').read_text())
(t/'Cargo.toml').write_text((old/'Cargo.toml').read_text().replace('name="product_pareto_discover"','name="global_prefix_simplify"'));assert'name="global_prefix_simplify"'in(t/'Cargo.toml').read_text();deps=json.loads((ex/'breakthrough-public1829-context-audit-20261020/SOURCE-FREEZE.json').read_bytes())['protected_files'];(r/'SOURCE-FREEZE.json').write_text(json.dumps({'tool_source_files':{n:sha((t/n).read_bytes())for n in ['Cargo.toml','Cargo.lock','io.rs','discover.rs']},'protected_files':deps,'expression_cap':1024,'input_streams':{'public1829':'16567ee18910b8ee9f7aca60c33f0aa88df9679e6528fa5a7884e74e1a877baf','official_de8':'131712cc9c79e9ffd3ac60c07d097a29b5252c03afa95c891c5ecdd603c60c2e'},'native_controls':13,'scope':'Global complete-prefix exact Boolean replay, registered inputs arbitrary/helperzero, fresh opaque limits conservative. Remove provenzero CCX/CCZ or lower CCX with exact linear/classical alias/complement. Original state replay; no phase, random-word or classical register changes. Component only, no gate/nonce/score.'},indent=2)+'\n');(r/'.gitignore').write_text('local-tool/\n__pycache__/\n*.ops.bin\n');(r/'.gitattributes').write_text('* -text\n')
(r/'run.py').write_text('''import hashlib,json,resource,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;f=json.loads((r/'SOURCE-FREEZE.json').read_text());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert all(sha(r/'local-tool'/p)==h for p,h in f['tool_source_files'].items());deps=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-protected';assert all(sha(deps/p)==h for p,h in f['protected_files'].items());exe=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-tool/target/release/global_prefix_simplify';stats=r.parent/'breakthrough-public1829-width-port-local-v4-20261020/stats-tool/target/release/native_width_stats';results={}
def limits():resource.setrlimit(resource.RLIMIT_AS,(5*1024**3,5*1024**3));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
for name,path in [('public1829',r.parent/'breakthrough-public1829-width-port-local-v4-20261020/public/ops.bin'),('official_de8',r.parent/'breakthrough-local-de8-replay-20261020/candidate/ops.bin')]:
 if name=='official_de8':
  deadline=time.monotonic()+1800
  while not(r.parent/'breakthrough-local-de8-replay-20261020/run.exit').exists():assert time.monotonic()<deadline;time.sleep(2)
  assert(r.parent/'breakthrough-local-de8-replay-20261020/run.exit').read_text().strip()=='0'
 assert sha(path)==f['input_streams'][name];start=time.monotonic()
 with(r/(name+'.log')).open('xb')as log:
  p=subprocess.Popen(['timeout','900',str(exe),str(path),str(r/name)],stdout=log,stderr=subprocess.STDOUT,preexec_fn=limits);(r/(name+'.pid')).write_text(str(p.pid)+'\\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\\n');row={'exit':rc,'seconds':time.monotonic()-start}
 if rc==0:
  report=json.loads((r/(name+'.json')).read_text());row.update(report)
  with(r/(name+'-stats.log')).open('xb')as log:subprocess.run([str(stats),str(r/(name+'.ops.bin')),str(r/(name+'-STATS.json'))],stdout=log,stderr=subprocess.STDOUT,check=True)
  row['output_sha256']=sha(r/(name+'.ops.bin'));row['static_diagnostics']=json.loads((r/(name+'-STATS.json')).read_text())
 results[name]=row;(r/'PROGRESS.json').write_text(json.dumps(results,indent=2)+'\\n')
(r/'RESULT.json').write_text(json.dumps({'status':'COMPONENT_GRID_COMPLETE_PRESERVE_RESOURCE_FAILURES_NOT_SCORED','native_controls':13,'cases':results,'scope':f['scope'],'binary_sha256':sha(exe)},indent=2)+'\\n')
''')
base='/mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments';(r/'run-local.sh').write_bytes(('''#!/bin/sh
set -eu
cd BASE/breakthrough-global-prefix-component-20261020
export RUSTC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustc
export RUSTDOC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustdoc
export RUSTUP_AUTO_INSTALL=0
export CARGO_HOME=/root/.cargo
export CARGO_BUILD_JOBS=2
export OMP_NUM_THREADS=1
export CARGO_TARGET_DIR=BASE/breakthrough-value-guard-fusion-audit-20261020/local-tool/target
trap 's=$?; printf "%s\\n" "$s" > run.exit' EXIT
/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo test --release --locked --manifest-path local-tool/Cargo.toml --bin global_prefix_simplify -- --nocapture > tests.log 2>&1
grep -q 'test result: ok. 13 passed; 0 failed;' tests.log
/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo build --release --locked --manifest-path local-tool/Cargo.toml --bin global_prefix_simplify > build.log 2>&1
python3 run.py
'''.replace('BASE',base)).encode());(r/'PLAN.md').write_text('''# Global exact prefix simplification on both current independent parents

Fixed source-bound inputs public1829 andcurrentofficialde8. Replay all original
operations from actual registered inputs arbitrary/helperszero, retaining exact
XOR expressions/fullkey products. Expressioncap1024 introduces distinct opaque
atoms, losing precision only. Remove CCX/CCZ only if effective operation always
zero; lower CCX toX/CX orclassically controlledCX only on exact symbol equality.
All phases preserved by action equality, all original RNG draws unchanged.
Original fullstate replay drives later proofs, so rewrites compose inductively.

Keep9prior native phase/guard/RNG/fault controls plus4new global basis/phase/
classicalalias/complement/HMR/late-register/opaque/fault controls (13total).
5GiBaddress/900s per source, preserve resource failures separately. No scorer
or harness changes, no gate, nonce, benchmark or quantumresource claim. Any
useful result needs self-contained literal source/prefix bindings/native/fresh
development/OWN finalgate/qualified ascendingnonce/full unchangedbenchmark and
automatic challenge verification before a record. Extra width zero.
''');print(r.name)
