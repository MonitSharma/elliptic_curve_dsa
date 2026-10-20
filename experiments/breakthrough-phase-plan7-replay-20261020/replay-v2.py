import hashlib,json,statistics,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;tool=ws/'breakthrough-output-audit-20261020';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();f=json.loads((tool/'TOOL-SOURCE-FREEZE-v2.json').read_text())
assert all(sha(tool/'tool-v2'/p)==h for p,h in f['source_files'].items());assert all(sha(Path(p))==h for p,h in f['protected_dependency_files'].items())
binary=tool/'tool/target/release/product_paired_diagnostic';assert sha(binary)=='add4bb5fd5a63cca8d565c28e8f4f5e43a34a34cc81ec22eb43a846c1aa25901'
original=ws/'simd-census-v2-20261016/bin/simd_census_v2';assert sha(original)=='790e92266ea67ec54ef701b2deed76fe8d0b766b411ca9eab877f82ae2c11a66'
croot=ws/'breakthrough-phase-pebble-plan7-20261020';cf=json.loads((croot/'SOURCE_FREEZE.json').read_text());assert(croot/'run.exit').read_text().strip()=='0'
assert all(sha(croot/'observer'/p)==h for p,h in{**cf['source_files'],**cf['protected_files']}.items())
streams={'parent':(croot/'cap1234/ops.bin','13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b'),'candidate':(croot/'cap1233/ops.bin','0bd52235bc2294d67fff45bb21e4f47c6559db09830e3e6654c42c85b5014c1a')};assert all(sha(p)==h for p,h in streams.values())
label='breakthrough-phase-pebble-plan7-dev-v1';batches=512
v1root=r;r=r/'attempt-v2';r.mkdir(exist_ok=False)
(r/'REPLAY-FREEZE.json').write_text(json.dumps({'label':label,'batches':batches,'shots_per_batch':64,'workers':2,'protected_scalar_batches_per_run':8,'tool_freeze_sha256':sha(tool/'TOOL-SOURCE-FREEZE-v2.json'),'output_binary_sha256':sha(binary),'original_binary_sha256':sha(original),'candidate_source_freeze_sha256':sha(croot/'SOURCE_FREEZE.json'),'streams':{name:{'path':str(p),'sha256':h}for name,(p,h)in streams.items()},'scope':'Finite development only. Raw candidate remains actualQ1234 and cost rises. Exact historical raw parent13f6 for mechanism checking; current official record54fc is a separate final-gate parent. No finalgate, nonce or score.'},indent=2)+'\n')
records={}
for name,exe,path in[('original-parent',original,streams['parent'][0]),('parent',binary,streams['parent'][0]),('candidate',binary,streams['candidate'][0])]:
 with(r/(name+'.out')).open('xb')as out,(r/(name+'.err')).open('xb')as err:
  p=subprocess.Popen([str(exe),str(path),label,'0',str(batches),'2',str(r/(name+'.jsonl')),'8'],stdout=out,stderr=err);(r/(name+'.pid')).write_text(str(p.pid)+'\n');assert p.wait()==0
 rows=[json.loads(l)for l in(r/(name+'.jsonl')).read_text().splitlines()];assert len(rows)==batches;assert[x['batch']for x in rows]==list(range(batches));records[name]=rows
 if name=='original-parent':assert rows==[json.loads(l)for l in(v1root/'original-parent.jsonl').read_text().splitlines()]
 if name=='parent':assert[{k:v for k,v in x.items()if k not in['output_sha3_256','target_lane_hashes','other_lane_hashes']}for x in rows]==records['original-parent']
parent,candidate=records['parent'],records['candidate'];delta=[(b['toffoli']-a['toffoli'])/64 for a,b in zip(parent,candidate)]
different=[a['batch']for a,b in zip(parent,candidate)if a['output_sha3_256']!=b['output_sha3_256']]
target=[];other=[];pf=set();cfail=set()
for a,b in zip(parent,candidate):
 af={x['lane']for x in a['failures']if x['value']};bf={x['lane']for x in b['failures']if x['value']};pf|={(a['batch'],i)for i in af};cfail|={(b['batch'],i)for i in bf}
 for lane in range(64):
  if a['target_lane_hashes'][lane]!=b['target_lane_hashes'][lane]:target.append({'batch':a['batch'],'lane':lane,'parent_value_fails':lane in af,'candidate_value_fails':lane in bf})
  if a['other_lane_hashes'][lane]!=b['other_lane_hashes'][lane]:other.append({'batch':a['batch'],'lane':lane})
summary={name:{'value_shots':sum(x['value_shots']for x in rows),'phase_shots':sum(x['phase_shots']for x in rows),'dirty_shots':sum(x['dirty_shots']for x in rows),'failed_batches':sum(bool(x['failures'])for x in rows),'mean_executed_raw_toffoli':sum(x['toffoli']for x in rows)/(64*batches),'rows_sha256':sha(r/(name+'.jsonl'))}for name,rows in records.items()}
result={'status':'PAIRED_RAW_DEVELOPMENT_COMPLETE','label':label,'batches':batches,'shots_per_source':64*batches,'all_original_parent_fields_match':True,'all_four_final_register_hashes_match_including_failed_inputs':not different,'different_output_batches':different,'different_target_lanes':target,'different_other_lanes':other,'value_failing_shot_identities_equal':pf==cfail,'candidate_minus_parent_raw_mean_toffoli':statistics.mean(delta),'paired_standard_error':statistics.stdev(delta)/len(delta)**0.5,'summaries':summary,'scope':'Exact finite output observation and diagnostic raw cost; no all-input proof, complete resource score, final statistical gate, or nonce.'}
(r/'PAIRED-RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));assert not different and summary['candidate']['dirty_shots']==0
