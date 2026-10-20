from pathlib import Path
root=Path(__file__).resolve().parents[2];r=root/'experiments/breakthrough-groups-safe-finished-20261020';r.mkdir(exist_ok=False)
(r/'.gitattributes').write_text('* -text\n');(r/'.gitignore').write_text('candidate/\n__pycache__/\n*resource-preflight*\nevidence.tar.gz\n')
(r/'PLAN.md').write_text('''# Freeze the stronger full-tail grouped-square source

Select the predeclaredgroups-safe28-d8 native case by its resource result before
new inputs: source748 record prototype actualQ1464, diagnostic746373, exacta871
control reproduced,27 inherited native controls/groupplan/all square units and
deliberate junction fault verified. This is not a scored result. Keep28-bit
wrap witness, full259-bit correction tails, exact capped-square splits and
native inverse-leaf depth8; retain uniform+2/public140/native rail/G6.

Fix the mode, remove the research-only junction-fault branch from the grouped
module, bind every complete raw record, apply unchanged generic once, bind every
output prefix against independent prototype, appendnonce0. All17 protected
files identical. Nativegroupplan and fullsquare caller-contract controls repeat
before generation (six historical walk-domain edge diagnostics remain separate).
Own fresh fullpoint development/finalgate versus then-current officialT parent,
qualifiedascendingnonce, unchangedbenchmark/local review precede autosubmission.
No old cache/table/gate reuse, no new approximation or scored record here.
''')
(r/'prepare.py').write_text('''import hashlib,json,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;old=ws/'breakthrough-grouped-square-ports-20261020';t=r/'candidate';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert(old/'resumed.exit').read_text().strip()=='0';prior=json.loads((old/'SOURCE-FREEZE.json').read_text());result=json.loads((old/'RESULT.json').read_text());chosen=next(x for x in result['cases']if x['mode']=='groups-safe28-d8');assert chosen['exit']==0 and chosen['qubits']==1464 and chosen['diagnostic_weight']==746373.0;assert next(x for x in result['cases']if x['mode']=='control')['stream_sha256']=='a871e42c3a40aa7fe228f68b8024a7167e57cdafbfd6732e19b650d2e6f845b9';assert all(sha(old/'observer'/path)==h for path,h in{**prior['source_files'],**prior['protected_files']}.items());rawstats=json.loads((old/'groups-safe28-d8-raw-stats.json').read_text());outstats=json.loads((old/'groups-safe28-d8-output-stats.json').read_text());assert sha(old/'groups-safe28-d8/ops.bin')==chosen['stream_sha256'];assert sha(old/'groups-safe28-d8/raw.ops.bin')==chosen['raw_stream_sha256']
h=hashlib.sha3_256();pos=0;path=old/'groups-safe28-d8/ops.bin'
with path.open('rb',buffering=0)as data:
 header=data.read(16);n=int.from_bytes(header[8:],'little');assert n==outstats['operations'];stop=(n-96)*56;child=subprocess.Popen(['zstd','-dc'],stdin=data,stdout=subprocess.PIPE)
 while block:=child.stdout.read(1<<20):
  if pos<stop:h.update(block[:min(len(block),stop-pos)])
  pos+=len(block)
 assert child.wait()==0 and pos==n*56
outputhash=h.hexdigest();assert not t.exists();subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),prior['base']],check=True)
for source_path in prior['source_files']:dest=t/source_path;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(old/'observer'/source_path,dest)
chain='src/point_add/sqc/chain_groups.rs';original=subprocess.check_output(['git','-C',str(ws/'toffoli'),'show',prior['upstream_public_group_source']+':'+chain]);assert hashlib.sha256(original).hexdigest()==prior['upstream_public_files'][chain];(t/chain).write_bytes(original+b'\\n'+(old/'group-tests.rs').read_bytes())
path=t/'src/point_add/mod.rs';body=path.read_bytes();needle=b'let square_mode=std::env::var("GROUPED_SQUARE_RESEARCH").expect("Declared grouped-square case");';assert body.count(needle)==1;body=body.replace(needle,b'let square_mode="groups-safe28-d8".to_owned();');needle=b'    exact_native_port::run(ops)';assert body.count(needle)==1;body=body.replace(needle,b'    groups_safe_finished::run(ops)');body+=b'\\nmod groups_safe_finished;\\n';path.write_bytes(body)
runtime='use crate::circuit::{Op,OperationType,QubitId};use sha3::{Digest,Sha3_256};\\npub(super)const IDENTITY_NONCE:u64=0;\\nfn bind(ops:&[Op],n:usize,want:&str){assert_eq!(ops.len(),n);let mut h=Sha3_256::new();for o in ops{for v in[o.kind as u64,o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{h.update(v.to_le_bytes());}}assert_eq!(format!("{:x}",h.finalize()),want,"Every grouped-safe raw/output record");}\\npub(super)fn run(ops:Vec<Op>)->Vec<Op>{bind(&ops,'+str(rawstats['operations'])+',"'+rawstats['records_sha3']+'");let mut ops=super::breakthrough_generic::run(ops);bind(&ops,'+str(n-96)+',"'+outputhash+'");assert!(IDENTITY_NONCE<(1u64<<48));for bit in 0..48{let mut o=Op::empty();o.kind=OperationType::X;o.q_target=QubitId((IDENTITY_NONCE>>bit)&1);o.validate();ops.extend([o,o]);}ops}\\n';(t/'src/point_add/groups_safe_finished.rs').write_text(runtime);assert all(sha(t/path)==h for path,h in prior['protected_files'].items());assert all(sha(t/path)==h for path,h in prior['source_files'].items()if path not in['src/point_add/mod.rs',chain]);subprocess.run(['cp','-a','--reflink=auto',str(old/'observer/target'),str(t/'target')],check=True);subprocess.run(['git','-C',str(t),'add','--intent-to-add','src/point_add'],check=True);(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD','--','src/point_add']));freeze={'base':prior['base'],'source_files':{path.relative_to(t).as_posix():sha(path)for path in(t/'src/point_add').rglob('*')if path.is_file()},'protected_files':prior['protected_files'],'identity_nonce':0,'fixed_mode':'groups-safe28-d8','raw_count':rawstats['operations'],'raw_records_sha3':rawstats['records_sha3'],'output_prefix_count':n-96,'output_prefix_records_sha3':outputhash,'expected_output_count':n,'expected_output_records_sha3':outstats['records_sha3'],'expected_output_compressed_sha256':chosen['stream_sha256'],'prototype_freeze_sha256':sha(old/'SOURCE-FREEZE.json'),'prototype_result_sha256':sha(old/'RESULT.json'),'new_square_public_component_source':prior['upstream_public_group_source'],'scope':'Fixed full259-correction/28-bit-witness/grouped-native square with exact capped splits and depth8inverseleaf on unchanged strengthenedT circuit; complete raw/output bindings, genericonce,nonce0, no research faultbranch/externaldump. Own finalgate/nonce/benchmark still required.'};(r/'SOURCE-FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\\n')
''')
(r/'run.py').write_text('''import hashlib,json,os,re,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'candidate';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();env=dict(os.environ,PEBBLE_HARD_CAP='1234')
def run(cmd,name,cwd=t,extra=None):
 with(r/(name+'.log')).open('xb')as out:p=subprocess.Popen(cmd,cwd=cwd,env=dict(env,**(extra or{})),stdout=out,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\\n');assert rc==0,name
try:
 run(['python3','prepare.py'],'prepare',r);f=json.loads((r/'SOURCE-FREEZE.json').read_text());run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit','grouped_plan_shape_tests','--','--nocapture','--test-threads=1'],'group-plan-tests');run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit','g3_square_unit','--','--nocapture','--test-threads=1'],'square-unit',extra={'G3_UT_PINS':'PEBBLE_HARD_CAP=1536;SQC_G1M=1;SQC_T=28;SQC_G=259;SQC_LEAF_D=8;G3_SQ_EXACT_SPLIT=1','G3_UT_CAP':'1408','G3_UT_BATCHES':'16','G3_UT_SEED':'grouped-safe-finished-native-20261020-v1'});assert all('test result: ok. 1 passed; 0 failed;'in(r/(n+'.log')).read_text()for n in['group-plan-tests','square-unit']);run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','build_circuit'],'build');start=time.time();run(['timeout','1800',str(t/'target/release/build_circuit')],'generate');assert all(sha(t/path)==h for path,h in{**f['source_files'],**f['protected_files']}.items());assert sha(t/'ops.bin')==f['expected_output_compressed_sha256'];stages=re.findall(r'^GENERIC_STAGE[^\\n]+',(r/'generate.log').read_text(),re.M);last=stages[-1];result={'status':'GROUPED_SAFE28_FULL259_FIXED_NONCE0_NOT_GATED_OR_SCORED','native_tests':2,'inherited_native_controls':27,'source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'stream_sha256':sha(t/'ops.bin'),'operations':f['expected_output_count'],'records_sha3':f['expected_output_records_sha3'],'qubits':int(re.search(r'nq=(\\d+)',last)[1]),'classical_bits':int(re.search(r'nb=(\\d+)',last)[1]),'diagnostic_weight':float(re.search(r'depth_weight=([\\d.]+)',last)[1]),'seconds':time.time()-start,'scope':f['scope']};(r/'RESULT.json').write_text(json.dumps(result,indent=2)+'\\n');(r/'run.exit').write_text('0\\n');print(json.dumps(result),flush=True)
except Exception:
 (r/'run.exit').write_text('1\\n');raise
''');print(r)
