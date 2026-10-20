from pathlib import Path
import ast,shutil
a=Path(__file__).parent;ex=a.parent;r=ex/'breakthrough-exact-witness-ripple-20261020';r.mkdir(exist_ok=False)
old=ex/'breakthrough-grouped-exact-resource-grid-v2-20261020'
for n in ['.gitattributes','.gitignore']:shutil.copyfile(old/n,r/n)
prepare='''import hashlib,json,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;old=ws/'breakthrough-grouped-exact-resource-grid-v2-20261020';t=r/'observer';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();f=json.loads((old/'SOURCE-FREEZE.json').read_text());assert all(sha(old/'observer'/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());assert(old/'run.exit').read_text().strip()=='0';assert not t.exists();subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in f['source_files']:
 dest=t/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(old/'observer'/p,dest)
public='3eefcf216ca37cba0ae3f56212d6b1302844a249';upstream=subprocess.check_output(['git','-C',str(ws/'toffoli'),'show',public+':src/point_add/sqc.rs']).decode();part=upstream[upstream.index('fn witness_product('):];assert part.count('(0..59)')==1 and part.count('sub_line(c,&reg[..59],&ops)+4')==1;part=part.replace('(0..59)','(0..reg.len())').replace('sub_line(c,&reg[..59],&ops)+4','sub_line(c,reg,&ops)+4')
needle=' let ands=sub_line(c,reg,&ops)+4;';assert part.count(needle)==1;part=part.replace(needle,' if super::env_flag("EXACT_WITNESS_TEST_FAULT"){c.x(prod[0]);}\\n'+needle)
p=t/'src/point_add/sqc.rs';s=p.read_text();start=s.index('    for &(sft, neg) in &[(0usize, false), (4, false), (6, true), (10, false), (32, false)]');end=s.index('    c.x_all(&reg);',start);legacy=s[start:end];s=s[:start]+'    if super::env_flag("EXACT_WITNESS_RIPPLE"){assert!(g>=n,"Exact replacement requires every old tail fullwidth");ands+=witness_product(c,&reg,&w);}else{\\n'+legacy+'    }\\n'+s[end:];s=s.replace('fn erase_sum(c: &mut Builder','pub(super) fn erase_sum(c: &mut Builder');s+='\\n'+part+'\\n'+(r/'witness-tests.rs').read_text();p.write_text(s)
p=t/'src/point_add/square.rs';s=p.read_text();needle='    let mut sum = y_hi.to_vec();';assert s.count(needle)==1;s=s.replace(needle,'    let held_sum=if super::env_flag("EXACT_SQUARE_SHARED_SUM"){let q=circ.alloc_qubits(h);circ.cx_pairs(y_hi,&q);Some(q)}else{None};\\n    let mut sum=held_sum.as_ref().map(|q|q.to_vec()).unwrap_or_else(||y_hi.to_vec());');needle='    restore_square_sum(circ, y_lo, &sum);';assert s.count(needle)==1;s=s.replace(needle,'    if let Some(q)=held_sum{let a:Vec<_>=(0..sum.len()).map(|j|y_lo.get(j).copied()).collect();let b:Vec<_>=(0..sum.len()).map(|j|y_hi.get(j).copied()).collect();super::sqc::erase_sum(circ,&sum,&a,&b);for &wire in q.iter().rev(){circ.release_clean(wire);}}else{restore_square_sum(circ,y_lo,&sum);}');s+='\\n'+(r/'sum-tests.rs').read_text();p.write_text(s)
p=t/'src/point_add/mod.rs';s=p.read_text();modes=['groups-safe28-d12','ripple-d12','ripple-d12-wide','sharedsum-d12-wide','ripple-sharedsum-d12-wide'];start=s.index('assert!(["control","groups-safe28-d8"');end=s.index('.contains(&square_mode.as_str()));',start)+len('.contains(&square_mode.as_str()));');s=s[:start]+'assert!('+json.dumps(modes)+'.contains(&square_mode.as_str()));'+s[end:];s=s.replace('square_mode.ends_with("walk1664")','square_mode.contains("wide")').replace('square_mode.ends_with("sq1536")','square_mode.contains("wide")');needle='    let mut ops = build_point_add();';assert s.count(needle)==1;s=s.replace(needle,'    std::env::set_var("EXACT_WITNESS_RIPPLE",if square_mode.contains("ripple"){"1"}else{"0"});std::env::set_var("EXACT_SQUARE_SHARED_SUM",if square_mode.contains("sharedsum"){"1"}else{"0"});std::env::set_var("EXACT_WITNESS_TEST_FAULT","0");\\n'+needle);p.write_text(s)
assert all(sha(t/p)==h for p,h in f['protected_files'].items());assert all(sha(t/p)==h for p,h in f['source_files'].items()if p not in['src/point_add/mod.rs','src/point_add/square.rs','src/point_add/sqc.rs']);subprocess.run(['cp','-a','--reflink=auto',str(old/'observer/target'),str(t/'target')],check=True);subprocess.run(['git','-C',str(t),'add','--intent-to-add','src/point_add'],check=True);(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD','--','src/point_add']));freeze={'base':f['base'],'source_files':{p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()},'protected_files':f['protected_files'],'parent_freeze_sha256':sha(old/'SOURCE-FREEZE.json'),'public_polynomial_source':public,'public_original_sqc_sha256':hashlib.sha256(upstream.encode()).hexdigest(),'adapted_fullwidth_function_sha256':hashlib.sha256(part.encode()).hexdigest(),'modes':modes,'control_expected_stream_sha256':'f8c83372543408f90dfad942341a03fff81876878af53815bdb7a99f62f7dc84','scope':'Exact witness product: old fiveFULL259-bit translations replaced by oneFULL259-bit subtraction of the same 3-bit witness times(2^32+977), public8-value polynomial extended to fullwidth. REQUIRE g>=n; no new cutoff. Separate exact sharedsum copy/freeerase; larger workspace allowed independentT objective. Strong28 witness/full259/alloriginalwindows/rounds/fullgroup tails/exactsplits unchanged. Fresh actual resource development/finalgate required later; no scored result.'};(r/'SOURCE-FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\\n')
''';ast.parse(prepare);(r/'prepare.py').write_text(prepare)
run='''import hashlib,json,os,re,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();env=dict(os.environ,PEBBLE_HARD_CAP='1664')
def run(args,name,cwd=t,extra=None):
 with(r/(name+'.log')).open('xb')as out:p=subprocess.Popen(args,cwd=cwd,env=dict(env,**(extra or{})),stdout=out,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\\n');return rc
try:
 assert run(['python3','prepare.py'],'prepare',r)==0;f=json.loads((r/'SOURCE-FREEZE.json').read_text())
 for filt,count in[('exact_witness_ripple_tests',3),('exact_shared_sum_tests',1),('grouped_plan_shape_tests',1)]:
  assert run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit',filt,'--','--nocapture','--test-threads=1'],'native-'+filt)==0;assert f'test result: ok. {count} passed; 0 failed;'in(r/('native-'+filt+'.log')).read_text()
 units=[]
 for mode in f['modes']:
  wide='wide'in mode;pins='PEBBLE_HARD_CAP='+('1664'if wide else'1536')+';SQC_G1M=1;SQC_T=28;SQC_G=259;SQC_LEAF_D=12;G3_SQ_EXACT_SPLIT=1;GROUP_JUNCTION_FAULT=0;EXACT_WITNESS_TEST_FAULT=0;EXACT_WITNESS_RIPPLE='+('1'if'ripple'in mode else'0')+';EXACT_SQUARE_SHARED_SUM='+('1'if'sharedsum'in mode else'0');name='square-unit-'+mode;rc=run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit','g3_square_unit','--','--nocapture','--test-threads=1'],name,extra={'G3_UT_PINS':pins,'G3_UT_CAP':'1536'if wide else'1408','G3_UT_BATCHES':'16','G3_UT_SEED':'exact-witness-full259-sharedsum-20261020-v1'});units.append({'mode':mode,'exit':rc,'historical_six_edge_exclusions_unchanged':True});assert rc==0,'Exact fullsquare caller contract failed'
 assert run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','build_circuit'],'build')==0;rows=[];stats=ws/'breakthrough-stackv3-width-stats-20261020/tool/target/release/native_width_stats'
 for mode in f['modes']:
  dest=r/mode;dest.mkdir();start=time.time();rc=run(['timeout','1800',str(t/'target/release/build_circuit')],'generate-'+mode,dest,{'GROUPED_SQUARE_RESEARCH':mode});row={'mode':mode,'exit':rc,'seconds':time.time()-start}
  if mode==f['modes'][0]:assert rc==0
  if rc==0:
   row['stream_sha256']=sha(dest/'ops.bin');row['raw_stream_sha256']=sha(dest/'raw.ops.bin');assert run([str(stats),str(dest/'ops.bin'),str(r/(mode+'-stats.json'))],'stats-'+mode,r)==0;st=json.loads((r/(mode+'-stats.json')).read_text());row['qubits']=st['qubits_protected_analyzer'];row['diagnostic_stats']=st
   if mode==f['modes'][0]:assert row['stream_sha256']==f['control_expected_stream_sha256']
  rows.append(row);(r/'PROGRESS.json').write_text(json.dumps(rows,indent=2)+'\\n');print(json.dumps({k:v for k,v in row.items()if k!='diagnostic_stats'}),flush=True)
 assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());(r/'RESULT.json').write_text(json.dumps({'status':'EXACT_ARITHMETIC_RESOURCE_GRID_NOT_GATED_OR_SCORED','native_components':4,'group_plan_controls':1,'fullsquare_units':units,'cases':rows},indent=2)+'\\n');(r/'run.exit').write_text('0\\n')
except BaseException:
 (r/'run.exit').write_text('1\\n');raise
''';ast.parse(run);(r/'run.py').write_text(run)
(r/'PLAN.md').write_text('''# Exact full259 witness consolidation and shared-sum grid

Declared fixed architecture cases before any new point inputs: reproduce
strong depth12precached f8c833; witnessripple at oldcap; witnessripplewide;
sharedsumwide; bothwide. Strong28witness,259correctiontails,fullgroup tails,
originalwindows/rounds andexactsplits stay. ExtraQ allowed forindependentT.

Old correction subtractsw,16w,1024w,2^32w andadds64w withALLtailsfull259.
Their translation equals -w*(2^32+977) modulo2^259. Public3eef's3-bit witness
polynomial supplies exact13lowbits of977w. Extend its one subtraction from
truncated59 toFULLreg.len()259; REQUIRE oldg>=n so no oldcut canbe silently
changed. No newpublic group/reduction/witness cut-off is imported. Polynomial
truth forw0..7, fullwidth old/new phase/value/dirty/guard tests anddeliberate
fault control precede fullsquare caller units andfullconstructor control.

Separate sharedsum uses128freshcopiedsum bits withbothparenthalves live,
then original exacterase_sum; componentbasis/phase/dirty andfullsquare tests.
Widecases global1664/square1536 topermit thisindependentT objective. Actual
protectedQ andstaticweights diagnostic only. Every source/protectedhash and
stream recorded. No pointdevelopment/finalgate/nonce/benchmark/score here.
Anyselectedcomplete source needs freshproof/fullbindings, development andown
solefinalgate vs exactthen-current officialT2bd before nonce/unchanged9024
benchmark/localverification/automatic GPT-6sol/Codex submission.
''');print(r)
