from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[2];r=root/'experiments/breakthrough-stackv3-plan7-generic-20261020';r.mkdir(exist_ok=False)
(r/'.gitattributes').write_text('* -text\n');(r/'.gitignore').write_text('candidate/\n__pycache__/\n*resource-preflight*\nevidence.tar.gz\n')
(r/'PLAN.md').write_text('''# Fixed stronger-witness native plan plus generic exact finishing

Wait for the separately frozen both-direction plan7 raw grid and protected
resource audit. Proceed only ifcap1233/t28 builds and measuresQ<=1233. Otherwise
record the construction failure without generating a candidate. No selection
by simulation inputs. Copy that exact native construction, fix mode1233/t28,
bind every raw record to its count and canonicalSHA3, then apply the unchanged
generic pipeline from officiald182 source9cb5de5f exactly once and nonce0 tail.
Copy its exact classical simplification modules and native tests; do not use
or edit the publicsource's old frozen tables. All17 protected files unchanged.
Freeze full source before generation and repeat native4 plus classical10.

This first output is a research source, pending fresh generic-output binding,
full512x64 development vs exactpublice3, own final failure-rate gate, qualified
ascending nonce and unchanged benchmark. Static proxy and nominal cap are not
scored results. No final gate/nonce screening is authorized by this script.
''')
(r/'run.py').write_text('''import hashlib,json,os,re,shutil,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;native=ws/'breakthrough-stackv3-width-plan7-both-20261020';stats=ws/'breakthrough-stackv3-plan7-both-stats-20261020';reference=ws/'breakthrough-native-both-final-20261020';t=r/'candidate';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(cmd,name,cwd=t,env=None):
 with(r/(name+'.log')).open('xb')as out:p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=out,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\\n');assert rc==0,name
try:
 started=time.time()
 while not(stats/'run.exit').exists():
  assert time.time()-started<7200;time.sleep(2)
 assert(stats/'run.exit').read_text().strip()=='0'and(native/'run.exit').read_text().strip()=='0'
 rows=json.loads((native/'RESULT.json').read_text())['cases'];row=next(x for x in rows if x['mode']=='cap1233-t28')
 if row['exit']:
  (r/'RESULT.json').write_text(json.dumps({'status':'NO_SUCCESSFUL_RAW1233_PRESERVE_CONSTRUCTION_FAILURE','exit':row['exit'],'native_source_freeze_sha256':sha(native/'SOURCE-FREEZE.json'),'scope':'No candidate constructed, no gate/nonce/benchmark.'},indent=2)+'\\n');(r/'run.exit').write_text('0\\n');raise SystemExit(0)
 stat=json.loads((stats/'cap1233-t28.json').read_text());assert stat['qubits_protected_analyzer']<=1233
 nf=json.loads((native/'SOURCE-FREEZE.json').read_text());rf=json.loads((reference/'SOURCE-FREEZE.json').read_text());src=reference/'candidate'
 assert all(sha(native/'observer'/p)==h for p,h in{**nf['source_files'],**nf['protected_files']}.items());assert all(sha(src/p)==h for p,h in{**rf['source_files'],**rf['protected_files']}.items());assert sha(native/'cap1233-t28/ops.bin')==row['stream_sha256'];assert not t.exists()
 subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),nf['base']],check=True)
 for p in nf['source_files']:dest=t/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(native/'observer'/p,dest)
 copied=['breakthrough_generic.rs','classical_factors_xor.rs','tests_classical_factors.rs']+[p.relative_to(src/'src/point_add').as_posix()for p in(src/'src/point_add/classical_wide').rglob('*')if p.is_file()]
 for p in copied:
  dest=t/'src/point_add'/p;assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src/'src/point_add'/p,dest)
 p=t/'src/point_add/mod.rs';s=p.read_bytes();needle=b'let mode=std::env::var("STACK_WIDTH_RESEARCH").expect("Declared fixed native width mode");';assert s.count(needle)==1;s=s.replace(needle,b'let mode="cap1233-t28".to_owned();');needle=b'if config.is_some(){return ops;}';assert s.count(needle)==1;s=s.replace(needle,b'if config.is_some(){return stack_plan7_generic::run(ops);}');s+=b'\\nmod breakthrough_generic;mod classical_factors_xor;mod classical_wide;mod stack_plan7_generic;\\n';p.write_bytes(s)
 runtime='use crate::circuit::{Op,OperationType,QubitId};use sha3::{Digest,Sha3_256};\\npub(super)const IDENTITY_NONCE:u64=0;\\npub(super)fn run(ops:Vec<Op>)->Vec<Op>{assert_eq!(ops.len(),'+str(stat['operations'])+');let mut h=Sha3_256::new();for o in &ops{for v in[o.kind as u64,o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{h.update(v.to_le_bytes());}}assert_eq!(format!("{:x}",h.finalize()),"'+stat['records_sha3']+'");let mut ops=super::breakthrough_generic::run(ops);assert!(IDENTITY_NONCE<(1u64<<48));for bit in 0..48{let mut o=Op::empty();o.kind=OperationType::X;o.q_target=QubitId((IDENTITY_NONCE>>bit)&1);o.validate();ops.extend([o,o]);}ops}\\n'
 (t/'src/point_add/stack_plan7_generic.rs').write_text(runtime);assert all(sha(t/p)==h for p,h in nf['protected_files'].items())
 subprocess.run(['cp','-a','--reflink=auto',str(native/'observer/target'),str(t/'target')],check=True);subprocess.run(['git','-C',str(t),'add','--intent-to-add','src/point_add'],check=True)
 (r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD','--','src/point_add']))
 f={'base':nf['base'],'source_files':{p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()},'protected_files':nf['protected_files'],'identity_nonce':0,'fixed_mode':'cap1233-t28','raw_count':stat['operations'],'raw_records_sha3':stat['records_sha3'],'native_source_freeze_sha256':sha(native/'SOURCE-FREEZE.json'),'stats_declaration_sha256':sha(stats/'INPUT-DECLARATION.json'),'reference_final_source_freeze_sha256':sha(reference/'SOURCE-FREEZE.json'),'copied_generic_files':copied,'scope':'Research fixed stronger28bit witness/loan128/native plan7 plus unchanged generic pipeline once, fullraw binding and nonce0. Not final-gated, output binding still required. No old table transplant, nonce screen, benchmark or scored result.'}
 (r/'SOURCE-FREEZE.json').write_text(json.dumps(f,indent=2)+'\\n');env=dict(os.environ,PEBBLE_HARD_CAP='1233');counts=[]
 for i,flt in enumerate(['stack_plan7_','classical_factors_xor::tests','classical_wide::']):
  name='tests-'+str(i);run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit',flt,'--','--nocapture','--test-threads=1'],name,env=env);ns=re.findall(r'test result: ok\\. (\\d+) passed; 0 failed;',(r/(name+'.log')).read_text());assert len(ns)==1;counts.append(int(ns[0]))
 assert counts==[4,3,7];run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','build_circuit'],'build',env=env);start=time.time();run(['timeout','1800',str(t/'target/release/build_circuit')],'generate',env=env);assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());stages=re.findall(r'^GENERIC_STAGE[^\\n]+',(r/'generate.log').read_text(),re.M);last=stages[-1];header=(t/'ops.bin').open('rb').read(16);assert header[:8]==b'QECCOPSZ'
 result={'status':'PLAN7_FIXED_GENERIC_RESEARCH_NOT_GATED_OR_SCORED','native_tests':sum(counts),'test_counts':counts,'source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'stream_sha256':sha(t/'ops.bin'),'operations':int.from_bytes(header[8:],'little'),'qubits':int(re.search(r'nq=(\\d+)',last)[1]),'classical_bits':int(re.search(r'nb=(\\d+)',last)[1]),'diagnostic_weight':float(re.search(r'depth_weight=([\\d.]+)',last)[1]),'stages':stages,'seconds':time.time()-start,'scope':f['scope']};(r/'RESULT.json').write_text(json.dumps(result,indent=2)+'\\n');(r/'run.exit').write_text('0\\n');print(json.dumps({k:v for k,v in result.items()if k!='stages'}),flush=True)
except Exception:
 (r/'run.exit').write_text('1\\n');raise
''')
print(r)
