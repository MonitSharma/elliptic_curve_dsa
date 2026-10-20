from pathlib import Path
root=Path(__file__).resolve().parents[2];r=root/'experiments/breakthrough-stackv3-width-stats-20261020';r.mkdir(exist_ok=False);(r/'.gitattributes').write_text('* -text\n');(r/'.gitignore').write_text('tool/\n__pycache__/\n*resource-preflight*\nevidence.tar.gz\n')
(r/'stats.rs').write_text('''mod io;use quantum_ecc::circuit::{OperationType as K,NO_BIT,analyze_ops};use sha3::{Digest,Sha3_256};
fn main(){let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),3);let ops=io::load_ops(&args[1]);let(mut depth,mut native,mut weight)=(0i32,0u64,0f64);let mut hash=Sha3_256::new();for o in &ops{for x in[o.kind as u64,o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{hash.update(x.to_le_bytes());}match o.kind{K::PushCondition=>depth+=1,K::PopCondition=>{depth-=1;assert!(depth>=0);},K::CCX|K::CCZ=>{native+=1;weight+=2f64.powi(-depth-i32::from(o.c_condition!=NO_BIT));},_=>{}}}assert_eq!(depth,0);let(nq,nb,_,_)=analyze_ops(ops.iter());let out=serde_json::json!({"status":"OPERATION_STREAM_STATIC_DIAGNOSTIC_ONLY","input":args[1],"operations":ops.len(),"qubits_protected_analyzer":nq,"classical_bits":nb,"native_toffoli":native,"fair_guard_depth_proxy":weight,"records_sha3":format!("{:x}",hash.finalize()),"scope":"Same guard-depth proxy as existing generic reporter. Not executed mean, not scored, no nonce/benchmark. Q is full protected analyzer over emitted records, never inferred from nominal cap."});std::fs::write(&args[2],serde_json::to_string_pretty(&out).unwrap()).unwrap();println!("{out}");}
''')
(r/'run.py').write_text('''import hashlib,json,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;old=ws/'breakthrough-context-lease-20261020';source=ws/'breakthrough-stackv3-width-20261020';t=r/'tool';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(cmd,name,cwd=t):
 with(r/(name+'.log')).open('xb')as out:p=subprocess.Popen(cmd,cwd=cwd,stdout=out,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\\n');assert rc==0,name
try:
 f=json.loads((old/'SOURCE-FREEZE.json').read_text());assert all(sha(old/'tool'/p)==h for p,h in f['tool_source_files'].items())and all(sha(Path(p))==h for p,h in f['protected_dependency_files'].items());assert(source/'run.exit').read_text().strip()=='0'and not t.exists();t.mkdir()
 for n in['Cargo.toml','Cargo.lock','io.rs']:shutil.copyfile(old/'tool'/n,t/n)
 shutil.copyfile(r/'stats.rs',t/'stats.rs');p=t/'Cargo.toml';p.write_bytes(p.read_bytes()+b'\\n[[bin]]\\nname="native_width_stats"\\npath="stats.rs"\\n');subprocess.run(['cp','-a','--reflink=auto',str(old/'tool/target'),str(t/'target')],check=True);inputs={row['mode']:source/row['mode']/'ops.bin'for row in json.loads((source/'RESULT.json').read_text())['cases']if row['exit']==0};freeze={'tool_source_files':{p.name:sha(p)for p in t.iterdir()if p.is_file()},'protected_dependency_files':f['protected_dependency_files'],'inputs':{n:{'path':str(p),'sha256':sha(p)}for n,p in inputs.items()},'scope':'Read-only protected analyze_ops and exact existing guard-depth diagnostic; no circuit change/gate/nonce/score.'};(r/'SOURCE-FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\\n');run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','native_width_stats'],'build');rows={}
 for n,p in inputs.items():assert sha(p)==freeze['inputs'][n]['sha256'];run([str(t/'target/release/native_width_stats'),str(p),str(r/(n+'.json'))],'stats-'+n);rows[n]=json.loads((r/(n+'.json')).read_text())
 assert all(sha(t/p)==h for p,h in freeze['tool_source_files'].items());(r/'RESULT.json').write_text(json.dumps({'status':'READ_ONLY_STATIC_WIDTH_PROXY_DIAGNOSTICS','cases':rows},indent=2)+'\\n');(r/'run.exit').write_text('0\\n')
except BaseException:
 (r/'run.exit').write_text('1\\n');raise
''');print(r)
