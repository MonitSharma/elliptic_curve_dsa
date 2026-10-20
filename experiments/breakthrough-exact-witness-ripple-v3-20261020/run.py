import hashlib,json,os,re,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();env=dict(os.environ,PEBBLE_HARD_CAP='1664')
def run(args,name,cwd=t,extra=None):
 with(r/(name+'.log')).open('xb')as out:p=subprocess.Popen(args,cwd=cwd,env=dict(env,**(extra or{})),stdout=out,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\n');return rc
try:
 assert run(['python3','prepare.py'],'prepare',r)==0;f=json.loads((r/'SOURCE-FREEZE.json').read_text())
 for filt,count in[('exact_witness_ripple_tests',4),('exact_shared_sum_tests',1),('grouped_plan_shape_tests',1)]:
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
  rows.append(row);(r/'PROGRESS.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps({k:v for k,v in row.items()if k!='diagnostic_stats'}),flush=True)
 assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());(r/'RESULT.json').write_text(json.dumps({'status':'EXACT_ARITHMETIC_RESOURCE_GRID_NOT_GATED_OR_SCORED','native_components':5,'group_plan_controls':1,'fullsquare_units':units,'cases':rows},indent=2)+'\n');(r/'run.exit').write_text('0\n')
except BaseException:
 (r/'run.exit').write_text('1\n');raise
