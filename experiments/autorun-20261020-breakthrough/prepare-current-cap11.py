from pathlib import Path
import hashlib,json,shutil
a=Path(__file__).resolve().parent;ex=a.parent;base=ex/'breakthrough-compact-generic-repeat-20261021';old=ex/'product-classical-cap11-20261019';r=ex/'breakthrough-current-cap11-20261021';r.mkdir(exist_ok=False);t=r/'local-tool';shutil.copytree(base/'local-tool',t)
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
shutil.copytree(t/'point_add/classical_wide',t/'point_add/control_wide')
pa=t/'point_add';p=pa/'classical_wide/mod.rs';p.write_text(p.read_text().replace('const SUPPORT_CAP: usize = 9;','const SUPPORT_CAP: usize = 11;'))
shutil.copyfile(old/'table.rs',pa/'classical_wide/table.rs');shutil.copyfile(old/'tests_table.rs',pa/'classical_wide/tests_table.rs')
(pa/'mod.rs').write_text('mod affine_simplify;mod quadratic_simplify;mod control_wide;mod classical_wide;\npub fn run(ops:Vec<crate::circuit::Op>,control:bool)->Vec<crate::circuit::Op>{if control{control_wide::simplify_classical(ops)}else{classical_wide::simplify_classical(ops)}}\n')
p=t/'Cargo.toml';p.write_text(p.read_text().replace('name = "compact_generic_repeat"','name = "current_cap11"'))
q=(ex/'breakthrough-flat-guard-control-20261021/discover.rs').read_text();q=q[q.index('fn qualify('):q.index('fn main(')]
q=q.replace('assert_eq!(a.stats,b.stats,"executed resource counts case{case}");','assert!(b.stats.toffoli_gates<=a.stats.toffoli_gates,"executed Toffolis may only decrease");').replace('FULL_PROTECTED_FLAT_GUARD_PASS','FULL_PROTECTED_CAP11_PASS').replace('executed T/Clifford count and all original random-word consumption match','original random-word consumption match; executed Toffolis do not increase')
s='use quantum_ecc::{circuit,sim,weierstrass_elliptic_curve};use circuit::Op;mod io;mod point_add;\n'+q+'''fn main(){let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),4);assert!(["control9","compat9","cap11"].contains(&a[3].as_str()));if a[3]=="compat9"{std::env::set_var("CLASSICAL_WIDE_CAP","9");}else{std::env::set_var("CLASSICAL_WIDE_CAP","11");}let ops=io::load_ops(&a[1]);let out=point_add::run(ops.clone(),a[3]=="control9");let q=qualify(&ops,&out);io::save_ops(&format!("{}.ops.bin",a[2]),&out);std::fs::write(format!("{}.json",a[2]),serde_json::to_string_pretty(&serde_json::json!({"status":"CURRENT_CAP11_EXACT_COMPONENT_NOT_A_SCORE","mode":a[3],"qualification":q})).unwrap()+"\\n").unwrap();}'''
(t/'discover.rs').write_text(s)
f=json.loads((base/'SOURCE-FREEZE.json').read_bytes());f.update(tool_source_files={p.relative_to(t).as_posix():sha(p)for p in t.rglob('*')if p.is_file()},input_streams={},scope='Fresh current-source eleven-atom exact classical table audit. Prior cap11 no-gain result on older classical12 input remains final. Independent unchanged original512-row control9 must byte-match expanded2048-row compat9 on each same new input before cap11. Every mode native and24complete protected arbitrary-input original quantum/classical/absolute-phase/RNG comparisons; executedT cannot increase. Only exact universal Boolean table identities, no sampled fingerprints or arithmetic cuts. No point gate/nonce/benchmark/record.')
(r/'SOURCE-FREEZE.json').write_text(json.dumps(f,indent=2)+'\n');(r/'PLAN.md').write_text(f['scope']+'\n');(r/'.gitignore').write_text('local-tool/\n*.ops.bin\n__pycache__/\n');(r/'.gitattributes').write_text('* -text\n')
runner='''import hashlib,json,resource,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;f=json.loads((r/'SOURCE-FREEZE.json').read_bytes());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert all(sha(r/'local-tool'/p)==h for p,h in f['tool_source_files'].items());deps=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-protected';assert all(sha(deps/p)==h for p,h in f['protected_files'].items())
parent=r.parent/'breakthrough-compact-generic-repeat-20261021';assert(parent/'run.exit').read_text().strip()=='0';pf=json.loads((parent/'RESULT.json').read_bytes());paths={n:parent/(n+'.ops.bin')for n in ['compact1233','compact1234']};inputs={n:sha(p)for n,p in paths.items()};(r/'INPUT-FREEZE.json').write_text(json.dumps({'streams':inputs,'parent_result_sha256':sha(parent/'RESULT.json'),'scope':'Input circuit streams frozen before any execution; no point inputs.'},indent=2)+'\\n')
exe=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-tool/target/release/current_cap11';stats=r.parent/'breakthrough-public1829-width-port-local-v4-20261020/stats-tool/target/release/native_width_stats';rows={}
def limits():resource.setrlimit(resource.RLIMIT_AS,(6*1024**3,6*1024**3));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
for n,p in paths.items():
 rr={}
 for mode in ['control9','compat9','cap11']:
  assert sha(p)==inputs[n];key=n+'-'+mode;start=time.monotonic()
  with(r/(key+'.log')).open('xb')as log:job=subprocess.Popen(['timeout','900',str(exe),str(p),str(r/key),mode],stdout=log,stderr=subprocess.STDOUT,preexec_fn=limits);(r/(key+'.pid')).write_text(str(job.pid)+'\\n');rc=job.wait()
  (r/(key+'.exit')).write_text(str(rc)+'\\n');assert rc==0,(n,mode,rc)
  output=r/(key+'.ops.bin');rr[mode]={'seconds':time.monotonic()-start,'output_sha256':sha(output),'protected':json.loads((r/(key+'.json')).read_bytes())['qualification']['protected_fullstream_comparisons']}
  if mode=='compat9':assert rr['control9']['output_sha256']==rr['compat9']['output_sha256'],'Independent cap9 stream control failed'
  if mode=='cap11':
   with(r/(key+'-stats.log')).open('xb')as log:subprocess.run([str(stats),str(output),str(r/(key+'-STATS.json'))],stdout=log,stderr=subprocess.STDOUT,check=True)
   rr[mode]['static_diagnostics']=json.loads((r/(key+'-STATS.json')).read_bytes())
  rows[n]=rr;(r/'PROGRESS.json').write_text(json.dumps(rows,indent=2)+'\\n')
(r/'RESULT.json').write_text(json.dumps({'status':'CURRENT_CAP11_COMPONENT_COMPLETE_NOT_SCORED','cases':rows,'binary_sha256':sha(exe),'scope':f['scope']},indent=2)+'\\n')
'''
(r/'run.py').write_text(runner)
s=(base/'run-local.sh').read_text().replace(base.name,r.name).replace('--bin compact_generic_repeat','--bin current_cap11')
# Source modules contain the original cap9 and new cap11 tests in separate namespaces.
(r/'run-local.sh').write_bytes(s.encode());print(r.name)
