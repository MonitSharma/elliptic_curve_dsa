from pathlib import Path
root=Path(__file__).resolve().parents[2];r=root/'experiments/breakthrough-grouped-square-ports-20261020';r.mkdir(exist_ok=False)
(r/'.gitattributes').write_text('* -text\n');(r/'.gitignore').write_text('observer/\n__pycache__/\n*resource-preflight*\nevidence.tar.gz\n')
(r/'PLAN.md').write_text('''# Exact grouped-square route on our stronger T circuit

New officialproduct acd0d88e/Q1234/T756265/source7499c902 supersedes e3. Its native
grouped C-row carry chains remove391Toffolis and restore full tails, removing
the old frozen221-edit table altogether. Do not transport any old table.

Three fixed native cases, frozen before any inputs: currentT control; newpublic
G1M/grouped square with28-bit witness, full259-bit correction tails, exact capped
square splits, leaf depth0; same with exact inverse-leaf depth8. Preserve our
current uniform+2/public140/native rail/G6 circuit and all17 protected files.
Import only publicsquare.rs (96 additions on our identical square source),
sqc.rs, sqleaf.rs and sqc/chain_groups.rs. Do not import public21-bit witness,
T0W/RT0W windows, retunes or source-bound table removals elsewhere. The new
square replaces its own conventional native construction; its sourceoffset
formula is imported with it. Force SQC_T28/SQC_G259/G3_SQ_EXACT_SPLIT1 in new
cases to strengthen all newly introduced finite correction/wrap windows.

Repeat27 prior exact native controls. Run the existing G3 square-unit contract
on all three fixed modes, cap1408,16x64 shots and fixedlabel; retain its six
explicitly excluded historical walk-domain edge diagnostics without universal
correctness claims. Independent structural control validates every grouped
carry parent/frame/flip, total9216ANDs and peak656, and detects a bad parent.
A deliberately removed-junction-flip group build must fail the square unit.
Then exact control must reproduce fulla871 nonce0 before new fullpoint sources
are generated. Every new raw and complete generic output is hashed/measured.
No gate/nonce/benchmark or scored result. A finished fixedsource and its own
whole-point finalgate against the current officialT record are mandatory.
''')
(r/'group-tests.rs').write_text(r'''
#[cfg(test)]mod grouped_plan_shape_tests{
use super::*;
fn check(rows:&[[i16;9]])->usize{let mut count=0;let mut last=0;for(i,r)in rows.iter().enumerate(){assert!(r[0]>=last&&r[0]<259);last=r[0];for(k,j)in[(r[1],r[2]),(r[3],r[4])]{if k==0{assert!((0..129).contains(&j));}else if k==1{assert!(j>=0&&(j as usize)<i);assert_ne!(rows[j as usize][8],0);assert!(rows[j as usize][1]>=0||rows[j as usize][3]>=0);}else{assert!(k<0);}}for j in[r[5],r[6],r[7]]{assert!(j<129);}assert!([0,1].contains(&r[8]));count+=usize::from(r[8]!=0&&(r[1]>=0||r[3]>=0));}assert_eq!(rows.last().unwrap()[0],258);assert_eq!(rows.last().unwrap()[8],0);count}
#[test]fn every_grouped_carry_parent_frame_and_full_tail_is_structurally_valid_and_bad_parent_is_detected(){let counts:Vec<_>=[G0,G1,G2,G3,G4,G5,G6,G7,G8,G9,G10,G11,G12,G13,G14,G15].iter().map(|r|check(r)).collect();assert_eq!(counts.iter().sum::<usize>(),9216);assert_eq!(*counts.iter().max().unwrap(),656);let mut bad=G0.to_vec();bad[1][3]=1;bad[1][4]=30000;assert!(std::panic::catch_unwind(||check(&bad)).is_err());}
}
''')
(r/'prepare.py').write_text('''import hashlib,json,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;old=ws/'breakthrough-native-both-final-20261020';t=r/'observer';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();sf=json.loads((old/'SOURCE-FREEZE.json').read_text());assert all(sha(old/'candidate'/p)==h for p,h in{**sf['source_files'],**sf['protected_files']}.items());base=sf['base'];public='7499c902d7989e5a995ccd2331104a532197851b';assert not t.exists();subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),base],check=True)
for p in sf['source_files']:dest=t/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(old/'candidate'/p,dest)
ported=['src/point_add/square.rs','src/point_add/sqc.rs','src/point_add/sqleaf.rs','src/point_add/sqc/chain_groups.rs'];upstream={}
for p in ported:
 data=subprocess.check_output(['git','-C',str(ws/'toffoli'),'show',public+':'+p]);upstream[p]=hashlib.sha256(data).hexdigest();dest=t/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
delta=subprocess.check_output(['git','-C',str(ws/'toffoli'),'diff','--numstat','fb2d03e8a70a8b69965710ef46c5cdce828e9ca2',public,'--','src/point_add/square.rs']).decode().strip();assert delta=='96\\t0\\tsrc/point_add/square.rs';(r/'public-square-port.patch').write_bytes(subprocess.check_output(['git','-C',str(ws/'toffoli'),'diff','fb2d03e8a70a8b69965710ef46c5cdce828e9ca2',public,'--','src/point_add/square.rs']))
p=t/'src/point_add/sqc/chain_groups.rs';raw=p.read_bytes();needle=b'.filter(|&&i|i>=0)';assert raw.count(needle)==1;raw=raw.replace(needle,b'.filter(|&&i|i>=0 && !std::env::var("GROUP_JUNCTION_FAULT").is_ok_and(|v|v=="1"))');raw+=b'\\n'+(r/'group-tests.rs').read_bytes();p.write_bytes(raw)
p=t/'src/point_add/mod.rs';raw=p.read_bytes();needle=b'    let mode="both".to_owned();';assert raw.count(needle)==1;raw=raw.replace(needle,needle+b'\\n    let square_mode=std::env::var("GROUPED_SQUARE_RESEARCH").expect("Declared grouped-square case");assert!(["control","groups-safe28-d0","groups-safe28-d8"].contains(&square_mode.as_str()));');needle=b'    let mut ops = build_point_add();';assert raw.count(needle)==1;raw=raw.replace(needle,b'    std::env::set_var("SQC_G1M",if square_mode=="control"{"0"}else{"1"});std::env::set_var("SQC_T","28");std::env::set_var("SQC_G","259");std::env::set_var("SQC_LEAF_D",if square_mode=="groups-safe28-d8"{"8"}else{"0"});std::env::set_var("GROUP_JUNCTION_FAULT","0");if square_mode!="control"{std::env::set_var("G3_SQ_EXACT_SPLIT","1");}\\n'+needle);needle=b'    native_both_finished::run(ops)';assert raw.count(needle)==1;raw=raw.replace(needle,b'    exact_native_port::run(ops)');raw+=b'\\nmod sqc;mod sqleaf;\\n';p.write_bytes(raw);assert all(sha(t/p)==h for p,h in sf['protected_files'].items());assert all(sha(t/p)==h for p,h in sf['source_files'].items()if p not in['src/point_add/mod.rs','src/point_add/square.rs']);subprocess.run(['cp','-a','--reflink=auto',str(old/'candidate/target'),str(t/'target')],check=True);subprocess.run(['git','-C',str(t),'add','--intent-to-add','src/point_add'],check=True);(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD','--','src/point_add']));f={'base':base,'source_files':{p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()},'protected_files':sf['protected_files'],'upstream_public_group_source':public,'upstream_public_files':upstream,'parent_final_source_freeze_sha256':sha(old/'SOURCE-FREEZE.json'),'modes':['control','groups-safe28-d0','groups-safe28-d8'],'fixed_new_witness_bits':28,'fixed_new_correction_tail_bits':259,'fixed_new_square_splits_exact':True,'control_expected_complete_nonce0_sha256':'a871e42c3a40aa7fe228f68b8024a7167e57cdafbfd6732e19b650d2e6f845b9','scope':'Research only: exact native grouped square/full correction tails/strong28bit witness on strengthened currentT construction, unchanged privategeneric once, rawcapture. No old bound table transport, no new window/error trade. Not final-gated or scored.'};(r/'SOURCE-FREEZE.json').write_text(json.dumps(f,indent=2)+'\\n')
''')
(r/'run.py').write_text('''import hashlib,json,os,re,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();env=dict(os.environ,PEBBLE_HARD_CAP='1234')
def run(cmd,name,cwd=t,extra=None):
 with(r/(name+'.log')).open('xb')as out:p=subprocess.Popen(cmd,cwd=cwd,env=dict(env,**(extra or{})),stdout=out,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\\n');return rc
try:
 assert run(['python3','prepare.py'],'prepare',r)==0;f=json.loads((r/'SOURCE-FREEZE.json').read_text());filters=['exact_strip_port_tests','prime_clean_pool_tests','wide_loan_policy_tests','reverse_budget_tests','fin1_fold_tests','t0_shared_product_tests','core_loan_fold_tests','phase_cubic_cap_tests','phase_pebble','phase_fit','phase_fusion','zero_carry','plan7_tests','terminal_contract_tests','terminal_birth_phase_tests','direct_transport_tests'];expected=[1,2,1,1,1,1,1,1,3,1,4,3,2,3,1,1]
 for i,(flt,n)in enumerate(zip(filters,expected)):
  name='tests-'+str(i);assert run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit',flt,'--','--nocapture','--test-threads=1'],name)==0;assert re.findall(r'test result: ok\\. (\\d+) passed; 0 failed;',(r/(name+'.log')).read_text())==[str(n)]
 assert run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit','grouped_plan_shape_tests','--','--nocapture','--test-threads=1'],'group-plan-tests')==0;assert 'test result: ok. 1 passed; 0 failed;'in(r/'group-plan-tests.log').read_text();unit=[]
 for mode in f['modes']:
  pins='SQC_G1M='+('0'if mode=='control'else'1')+';SQC_T=28;SQC_G=259;SQC_LEAF_D='+('8'if mode.endswith('d8')else'0')+';GROUP_JUNCTION_FAULT=0'+(''if mode=='control'else';G3_SQ_EXACT_SPLIT=1');params={'G3_UT_PINS':pins,'G3_UT_CAP':'1408','G3_UT_BATCHES':'16','G3_UT_SEED':'native-grouped-square-safe28-20261020-v1'};rc=run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit','g3_square_unit','--','--nocapture','--test-threads=1'],'square-unit-'+mode,extra=params);row={'mode':mode,'exit':rc,'historical_six_walk_domain_edges_excluded_by_existing_unit':True};log=(r/('square-unit-'+mode+'.log')).read_text();row['g3_summary']=re.findall(r'^G3_UT pins=[^\\n]+',log,re.M);row['edge_phase_masks']=re.findall(r'^G3_UT edge[^\\n]+',log,re.M);unit.append(row)
  if mode!='control':assert rc==0,'New grouped square must pass existing native unit contract before full construction'
 fault={'G3_UT_PINS':'SQC_G1M=1;SQC_T=28;SQC_G=259;SQC_LEAF_D=8;G3_SQ_EXACT_SPLIT=1;GROUP_JUNCTION_FAULT=1','G3_UT_CAP':'1408','G3_UT_BATCHES':'2','G3_UT_SEED':'native-grouped-square-junction-fault-20261020-v1'};rc=run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit','g3_square_unit','--','--nocapture','--test-threads=1'],'square-unit-junction-fault',extra=fault);assert rc==101 and 'G3_UT pins='in(r/'square-unit-junction-fault.log').read_text();(r/'NATIVE-CONTROLS.json').write_text(json.dumps({'prior_exact_native_controls':27,'group_plan_controls':1,'unit_cases':unit,'deliberate_junction_fault_exit':rc,'scope':'Existing G3 unit contract excludes its six documented walk-domain edges; their raw diagnostics retained. No universal arbitraryfield claim.'},indent=2)+'\\n');assert run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','build_circuit'],'build')==0;results=[];stats=ws/'breakthrough-stackv3-width-stats-20261020'
 for mode in f['modes']:
  dest=r/mode;dest.mkdir();start=time.time();rc=run(['timeout','1800',str(t/'target/release/build_circuit')],'generate-'+mode,dest,{'GROUPED_SQUARE_RESEARCH':mode});row={'mode':mode,'exit':rc,'seconds':time.time()-start}
  if rc:assert mode!='control','Exact currentT control failed; no source binding may be bypassed'
  else:
   row['stream_sha256']=sha(dest/'ops.bin');row['raw_stream_sha256']=sha(dest/'raw.ops.bin');stages=re.findall(r'^GENERIC_STAGE[^\\n]+',(r/('generate-'+mode+'.log')).read_text(),re.M);last=stages[-1];row['qubits']=int(re.search(r'nq=(\\d+)',last)[1]);row['diagnostic_weight']=float(re.search(r'depth_weight=([\\d.]+)',last)[1]);row['generic_stages']=stages
   if mode=='control':assert row['stream_sha256']==f['control_expected_complete_nonce0_sha256'],'Full a871 control must reproduce exactly'
   for tag,file in[('raw','raw.ops.bin'),('output','ops.bin')]:assert run([str(stats/'tool/target/release/native_width_stats'),str(dest/file),str(r/(mode+'-'+tag+'-stats.json'))],'stats-'+mode+'-'+tag,r)==0
  results.append(row);(r/'PROGRESS.json').write_text(json.dumps(results,indent=2)+'\\n');print(json.dumps({k:v for k,v in row.items()if k!='generic_stages'}),flush=True)
 assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());(r/'RESULT.json').write_text(json.dumps({'status':'GROUPED_SQUARE_NATIVE_FIXED_CASES_NOT_GATED_OR_SCORED','native_controls':28,'unit_cases':unit,'source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'cases':results},indent=2)+'\\n');(r/'run.exit').write_text('0\\n')
except Exception:
 (r/'run.exit').write_text('1\\n');raise
''');print(r)
