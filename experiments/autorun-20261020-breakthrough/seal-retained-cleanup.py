import hashlib,json,re,subprocess,tarfile
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'observer';assert r.name=='breakthrough-prefix-retained-cleanup-20261020'and(r/'run.exit').read_text().strip()=='0'and not(r/'EVIDENCE-MANIFEST.json').exists();sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();f=json.loads((r/'SOURCE-FREEZE.json').read_text());assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());result=json.loads((r/'RESULT.json').read_text());model=json.loads((r/'MODEL.json').read_text());assert result['native_test_counts']==[1,1,1,1,1,2,2,1,1,2]and len(result['cases'])==23
for i,n in enumerate(result['native_test_counts']):assert re.findall(r'test result: ok\. (\d+) passed; 0 failed;',(r/f'tests-{i}.log').read_text())==[str(n)]
assert model['frontier'][7]['core_ANDs']==35 and model['frontier'][7]['prefix_peak_helpers']==27 and 'count=7 ANDs=35 HMRs=35 peak_helpers=27'in(r/'tests-0.log').read_text();assert all(x['exit']==0 for x in result['cases'][:21])and all(x['exit']==101 for x in result['cases'][21:]);assert all('Prefix27 full fold needs at least8 ladder wires'in x['failure_tail']for x in result['cases'][21:])
receipt={'status':'NATIVE_COMPONENT_PASS_COMPLETE_RESOURCE_GRID_NONCOMPETITIVE','native_tests':13,'core_frontier_7':{'primary_inputs':14,'helpers_peak':27,'total_core_peak':41,'ANDs':35,'HMRs':35,'kept_across_ladder':27},'phase_controls':'All16384 inputs,3 guards, every independent measurement coefficient and fixed patterns for all12 frontier masks. Fullfold values/phase/ancillas match reference with independent upper words at24 tight-budget settings. Original11 controls also pass.','best_raw_case':result['cases'][4],'original_baseline_raw_diagnostic_weight':762230.75,'compact_no_retention_raw_diagnostic_weight':762282.5,'best_retained_raw_diagnostic_weight':762260.5,'remaining_raw_excess':29.75,'failed_cases':[{'index':x['index'],'keep':x['keep'],'room':x['room'],'reason':'Unchanged ladder minimum assertion; supported isolated fixture does not establish all complete contexts.'}for x in result['cases'][21:]],'source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'native_core_log_sha256':sha(r/'tests-0.log'),'native_fullfold_log_sha256':sha(r/'tests-1.log'),'scope':'Component success only, no complete point-add resource record, final failure gate, nonce or benchmark. All failed construction cases remain preserved. Next: read-only tick profiles to see whether independent local choices help.'};(r/'NATIVE-RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n')
changed=[]
for p,h in f['source_files'].items():
 prior=subprocess.run(['git','-C',str(t),'show',f['base']+':'+p],capture_output=True)
 if prior.returncode or hashlib.sha256(prior.stdout).hexdigest()!=h:changed.append(p)
with tarfile.open(r/'changed-point-add-source.tar.gz','w:gz')as a:
 for p in sorted(changed):a.add(t/p,arcname=p,recursive=False)
files={p.name:p for p in r.iterdir()if p.is_file()and'resource-preflight'not in p.name and p.name not in ['evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json']};streams={}
for case in r.glob('case*'):
 if case.is_dir():
  for p in case.iterdir():
   if not p.is_file():continue
   if p.name.endswith('ops.bin'):streams[p.relative_to(r).as_posix()]=sha(p)
   else:files[p.relative_to(r).as_posix()]=p
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps({'files':{p:sha(v)for p,v in files.items()},'streams_retained_on_server':streams,'changed_source_files':changed,'scope':receipt['scope']},indent=2)+'\n')
with tarfile.open(r/'evidence.tar.gz','w:gz')as a:
 for p,v in sorted(files.items()):a.add(v,arcname=p,recursive=False)
 a.add(r/'EVIDENCE-MANIFEST.json',arcname='EVIDENCE-MANIFEST.json',recursive=False)
(r/'PACKAGE-RESULT.json').write_text(json.dumps({'archive_sha256':sha(r/'evidence.tar.gz'),'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')},indent=2)+'\n');print(len(files)+1,'members sealed')
