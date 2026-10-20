import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((r/'TOOL-SOURCE-FREEZE-v2.json').read_text());v1=json.loads((r/'REPLAY-FREEZE.json').read_text())
assert all(sha(r/'tool-v2'/p)==h for p,h in f['source_files'].items());assert all(sha(Path(p))==h for p,h in f['protected_dependency_files'].items())
binary=r/'tool/target/release/product_paired_diagnostic';records={}
for name in['parent','candidate']:
 stream=Path(v1['streams'][name]['path']);assert sha(stream)==v1['streams'][name]['sha256']
 with(r/(name+'-v2.out')).open('xb')as out,(r/(name+'-v2.err')).open('xb')as err:
  p=subprocess.Popen([str(binary),str(stream),f['label'],'0',str(f['batches']),'2',str(r/(name+'-v2.jsonl')),'8'],stdout=out,stderr=err);(r/(name+'-v2.pid')).write_text(str(p.pid)+'\n');assert p.wait()==0
 rows=[json.loads(l)for l in(r/(name+'-v2.jsonl')).read_text().splitlines()];old=[json.loads(l)for l in(r/(name+'.jsonl')).read_text().splitlines()]
 assert[{k:v for k,v in row.items()if k not in['target_lane_hashes','other_lane_hashes']}for row in rows]==old
 assert all(len(row['target_lane_hashes'])==len(row['other_lane_hashes'])==64 for row in rows);records[name]=rows
def failures(row):return {entry['lane'] for entry in row['failures']if entry['value']}
diff_target=[];diff_other=[];parent_fail=set();candidate_fail=set()
for a,b in zip(records['parent'],records['candidate']):
 af,bf=failures(a),failures(b);parent_fail|={(a['batch'],lane)for lane in af};candidate_fail|={(b['batch'],lane)for lane in bf}
 for lane in range(64):
  if a['target_lane_hashes'][lane]!=b['target_lane_hashes'][lane]:diff_target.append({'batch':a['batch'],'lane':lane,'parent_value_fails':lane in af,'candidate_value_fails':lane in bf})
  if a['other_lane_hashes'][lane]!=b['other_lane_hashes'][lane]:diff_other.append({'batch':a['batch'],'lane':lane})
result={'status':'SAME_V1_FAILURE_CLASSIFIED_NO_CHANGED_CIRCUIT_OR_VERDICT','same_label_and_all_old_fields_reproduced':True,'value_failing_shot_identities_equal':parent_fail==candidate_fail,
 'different_target_lanes':diff_target,'different_other_lanes':diff_other,'target_differences_confined_to_both_value_failing':all(x['parent_value_fails']and x['candidate_value_fails']for x in diff_target),
 'observation_binary_sha256':sha(binary),'v1_binary_preserved_sha256':sha(r/'bin/output-v1'),'scope':'Classifies existing full-output hash mismatch on exactly the same512 batches. Does not establish its algorithmic cause or change the failed equivalence verdict. No final gate, nonce or scored result.'}
(r/'OUTPUT-DIFFERENCE-CLASSIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
