import hashlib,json,os,re,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();env=dict(os.environ,PEBBLE_HARD_CAP='1234')
def run(cmd,name,cwd=t,extra=None):
 with(r/(name+'.log')).open('xb')as out:p=subprocess.Popen(cmd,cwd=cwd,env=dict(env,**(extra or{})),stdout=out,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\n');return rc
try:
 assert(r/'run.exit').read_text().strip()=='1';f=json.loads((r/'SOURCE-FREEZE.json').read_text());assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());expected=[1,2,1,1,1,1,1,1,3,1,4,3,2,3,1,1]
 for i,n in enumerate(expected):assert re.findall(r'test result: ok\. (\d+) passed; 0 failed;',(r/('tests-'+str(i)+'.log')).read_text())==[str(n)]
 assert 'test result: ok. 1 passed; 0 failed;'in(r/'group-plan-tests.log').read_text();assert 'Independent phase-pebble cap: NotPresent'in(r/'square-unit-groups-safe28-d0.log').read_text();unit=[]
 for mode in f['modes']:
  pins='PEBBLE_HARD_CAP=1536;SQC_G1M='+('0'if mode=='control'else'1')+';SQC_T=28;SQC_G=259;SQC_LEAF_D='+('8'if mode.endswith('d8')else'0')+';GROUP_JUNCTION_FAULT=0'+(''if mode=='control'else';G3_SQ_EXACT_SPLIT=1');params={'G3_UT_PINS':pins,'G3_UT_CAP':'1408','G3_UT_BATCHES':'16','G3_UT_SEED':'native-grouped-square-safe28-20261020-v1'};rc=run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit','g3_square_unit','--','--nocapture','--test-threads=1'],'resumed-square-unit-'+mode,extra=params);row={'mode':mode,'exit':rc,'historical_six_walk_domain_edges_excluded_by_existing_unit':True};log=(r/('resumed-square-unit-'+mode+'.log')).read_text();row['g3_summary']=re.findall(r'^G3_UT pins=[^\n]+',log,re.M);row['edge_phase_masks']=re.findall(r'^G3_UT edge[^\n]+',log,re.M);unit.append(row)
  if mode!='control':assert rc==0,'New grouped square must pass existing native unit contract before full construction'
 fault={'G3_UT_PINS':'PEBBLE_HARD_CAP=1536;SQC_G1M=1;SQC_T=28;SQC_G=259;SQC_LEAF_D=8;G3_SQ_EXACT_SPLIT=1;GROUP_JUNCTION_FAULT=1','G3_UT_CAP':'1408','G3_UT_BATCHES':'2','G3_UT_SEED':'native-grouped-square-junction-fault-20261020-v1'};rc=run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit','g3_square_unit','--','--nocapture','--test-threads=1'],'resumed-square-unit-junction-fault',extra=fault);assert rc==101 and 'G3_UT pins='in(r/'resumed-square-unit-junction-fault.log').read_text();(r/'NATIVE-CONTROLS.json').write_text(json.dumps({'prior_exact_native_controls':27,'group_plan_controls':1,'unit_cases':unit,'deliberate_junction_fault_exit':rc,'scope':'Existing G3 unit contract excludes its six documented walk-domain edges; their raw diagnostics retained. No universal arbitraryfield claim.'},indent=2)+'\n');assert run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','build_circuit'],'resumed-build')==0;results=[];stats=ws/'breakthrough-stackv3-width-stats-20261020'
 for mode in f['modes']:
  dest=r/mode;dest.mkdir();start=time.time();rc=run(['timeout','1800',str(t/'target/release/build_circuit')],'resumed-generate-'+mode,dest,{'GROUPED_SQUARE_RESEARCH':mode});row={'mode':mode,'exit':rc,'seconds':time.time()-start}
  if rc:assert mode!='control','Exact currentT control failed; no source binding may be bypassed'
  else:
   row['stream_sha256']=sha(dest/'ops.bin');row['raw_stream_sha256']=sha(dest/'raw.ops.bin');stages=re.findall(r'^GENERIC_STAGE[^\n]+',(r/('resumed-generate-'+mode+'.log')).read_text(),re.M);last=stages[-1];row['qubits']=int(re.search(r'nq=(\d+)',last)[1]);row['diagnostic_weight']=float(re.search(r'depth_weight=([\d.]+)',last)[1]);row['generic_stages']=stages
   if mode=='control':assert row['stream_sha256']==f['control_expected_complete_nonce0_sha256'],'Full a871 control must reproduce exactly'
   for tag,file in[('raw','raw.ops.bin'),('output','ops.bin')]:assert run([str(stats/'tool/target/release/native_width_stats'),str(dest/file),str(r/(mode+'-'+tag+'-stats.json'))],'resumed-stats-'+mode+'-'+tag,r)==0
  results.append(row);(r/'PROGRESS.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps({k:v for k,v in row.items()if k!='generic_stages'}),flush=True)
 assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());(r/'RESULT.json').write_text(json.dumps({'status':'GROUPED_SQUARE_NATIVE_FIXED_CASES_NOT_GATED_OR_SCORED','native_controls':28,'unit_cases':unit,'source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'cases':results},indent=2)+'\n');(r/'resumed.exit').write_text('0\n')
except Exception:
 (r/'resumed.exit').write_text('1\n');raise
