import hashlib,json,statistics,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;f=json.loads((r/'TOOL-SOURCE-FREEZE.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert all(sha(r/'tool'/p)==h for p,h in f['source_files'].items());assert all(sha(Path(p))==h for p,h in f['protected_dependency_files'].items())
original=ws/'simd-census-v2-20261016/bin/simd_census_v2';assert sha(original)==f['original_binary_sha256']
binary=r/'tool/target/release'/f['binary_name'];binary_sha=sha(binary)
candidate_root=ws/'breakthrough-local-fold-20261020';cf=json.loads((candidate_root/'SOURCE_FREEZE.json').read_text())
assert(candidate_root/'run.exit').read_text().strip()=='0'
assert all(sha(candidate_root/'observer'/p)==h for p,h in{**cf['source_files'],**cf['protected_files']}.items())
streams={'parent':(candidate_root/'cap1234/ops.bin','13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b'),
 'candidate':(candidate_root/'cap1233/ops.bin','932f51840b6c49501a193e540f4e5a2d3150a4c4be0129742a103a09497570df')}
assert all(sha(path)==expected for path,expected in streams.values())
(r/'REPLAY-FREEZE.json').write_text(json.dumps({'label':f['label'],'batches':f['batches'],'original_binary_sha256':sha(original),'output_binary_sha256':binary_sha,
 'streams':{name:{'path':str(path),'sha256':expected}for name,(path,expected)in streams.items()},'candidate_source_freeze_sha256':sha(candidate_root/'SOURCE_FREEZE.json'),'scope':'Development only; complete candidate stillQ1234 and extraT, no resource improvement/final gate.'},indent=2)+'\n')
records={}
for name,exe,stream in[('original-parent',original,streams['parent'][0]),('parent',binary,streams['parent'][0]),('candidate',binary,streams['candidate'][0])]:
 with(r/(name+'.out')).open('xb')as out,(r/(name+'.err')).open('xb')as err:
  p=subprocess.Popen([str(exe),str(stream),f['label'],'0',str(f['batches']),str(f['workers']),str(r/(name+'.jsonl')),str(f['protected_scalar_batches_per_run'])],stdout=out,stderr=err)
  (r/(name+'.pid')).write_text(str(p.pid)+'\n');assert p.wait()==0
 rows=[json.loads(l)for l in(r/(name+'.jsonl')).read_text().splitlines()];assert len(rows)==f['batches'];assert [x['batch']for x in rows]==list(range(f['batches']))
 records[name]=rows
 if name=='parent':assert [{k:v for k,v in row.items()if k!='output_sha3_256'}for row in rows]==records['original-parent']
parent,candidate=records['parent'],records['candidate'];diff=[(b['toffoli']-a['toffoli'])/64 for a,b in zip(parent,candidate)]
different=[a['batch']for a,b in zip(parent,candidate)if a['output_sha3_256']!=b['output_sha3_256']]
summary={name:{'value_shots':sum(x['value_shots']for x in rows),'phase_shots':sum(x['phase_shots']for x in rows),'dirty_shots':sum(x['dirty_shots']for x in rows),'failed_batches':sum(bool(x['failures'])for x in rows),'mean_executed_raw_toffoli':sum(x['toffoli']for x in rows)/(64*f['batches']),'rows_sha256':sha(r/(name+'.jsonl'))}for name,rows in records.items()}
result={'status':'OUTPUT_HASH_DEVELOPMENT_DIAGNOSTIC_COMPLETE','label':f['label'],'batches':f['batches'],'shots_per_source':64*f['batches'],
 'every_original_parent_row_field_matches':True,'all_four_final_register_hashes_match_including_failed_inputs':not different,'different_output_batches':different,
 'candidate_minus_parent_raw_mean_toffoli':statistics.mean(diff),'paired_standard_error':statistics.stdev(diff)/len(diff)**0.5,'summaries':summary,
 'protected_scalar_verified_batches_per_run':8,'output_binary_sha256':binary_sha,'scope':'Finite paired development diagnostic, including inherited failing outputs. SHA3-256 equality is not a universal proof. No complete scored improvement, final gate, nonce or official benchmark.'}
(r/'OUTPUT-DIAGNOSTIC.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
assert not different and summary['candidate']['dirty_shots']==0
