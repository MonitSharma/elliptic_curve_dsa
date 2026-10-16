from pathlib import Path
import collections,hashlib,json,math,statistics,tarfile

R=Path(__file__).resolve().parent;E=R.parent;I=R/'inputs'
sha=lambda b:hashlib.sha256(b).hexdigest()
file_sha=lambda p:sha(p.read_bytes())
audit=json.loads((I/'ROOT_TERMINAL_AUDIT.json').read_text())
assert (I/'terminal-audit.exit').read_text().strip()=='0'
assert (I/'search.exit').read_text().strip()=='0'
assert (I/'ROOT_TERMINAL_AUDIT.json').read_bytes()==(I/'terminal-audit.log').read_bytes()
assert file_sha(I/'audit-terminal.py')==audit['audit_source_sha256']=='70dd1d4378b498600027aefabbe7e170a2c356a9a9571773766aa148d768348e'
accept=json.loads((I/'ACCEPTANCE.json').read_text());run=json.loads((I/'run-record.json').read_text());result=json.loads((I/'RESULT.json').read_text())
assert file_sha(I/'ACCEPTANCE.json')==run['acceptance_sha256']=='2c33d3e2b19cd77b8069e4c134f162e2ee0c9d8d7b97aa57ce4f56d388693682'
assert result['worker_exit_codes']==[0]*4 and not result['deadline_stop']
assert audit['status']=='LOWEST_PASS_COMPLETE_JSONL_AUDIT_PASS'
rows=[11866112,11862016,11862016,11862016]
for lane,expected in enumerate(rows):
 assert (I/f'worker{lane}.exit').read_text().strip()=='0'
 progress=json.loads((I/f'worker{lane}-progress.json').read_text());assert progress==result['progress'][lane]
 assert progress['cumulative_worker_rows']==audit['lanes'][lane]['rows']==expected
 assert sum(audit['lanes'][lane]['dispositions'].values())==expected
 assert audit['lanes'][lane]['complete_local_prefix']
 assert progress['first']==1+((expected//4096-1)*4+lane)*4096
 assert progress['last']==progress['first']+4095
prefix=min((n//4096)*4+lane for lane,n in enumerate(rows))*4096
assert prefix==sum(rows)==audit['complete_global_prefix']==audit['operational_unique_nonces']==47452160
assert [n for lane in audit['lanes']for n in lane['passes']]==[47449113]
saved=json.loads((I/'pass-47449113.json').read_text());assert saved['nonce']==47449113 and saved['full_protected9024_pass']is True
assert audit['lowest_full_protected_pass']==result['best_full_protected_pass']==47449113
assert audit['operational_overrun_above_lowest']==prefix-47449113==3047
for path,h in accept['runtime_artifacts'].items():assert audit['runtime_artifacts_rehashed'][path]==h

def archive_review(folder,expected_hash=None):
 path=E/folder/'evidence.tar.gz';h=file_sha(path)
 if expected_hash:assert h==expected_hash
 with tarfile.open(path)as tar:
  names=tar.getnames();manifest_name='MANIFEST.json'if'MANIFEST.json'in names else'manifest.json'
  manifest=json.loads(tar.extractfile(manifest_name).read())
  for name,expected in manifest.items():assert sha(tar.extractfile(name).read())==expected,(folder,name)
  data={name:tar.extractfile(name).read()for name in names if name.endswith('.jsonl')}
  summary={'folder':folder,'archive_sha256':h,'verified_members':len(manifest),'rowfiles':[]}
  union=set()
  for name,body in data.items():
   parsed=list(map(json.loads,body.splitlines()));nonces=[x['nonce']for x in parsed]
   assert len(set(nonces))==len(nonces),(folder,name)
   union.update(nonces)
   summary['rowfiles'].append({'name':name,'rows':len(nonces),'minimum_nonce':min(nonces),'maximum_nonce':max(nonces),'sha256':sha(body)})
  summary.update(complete_nonce_row_attempts=sum(x['rows']for x in summary['rowfiles']),distinct_nonces=len(union))
  summary['result']=json.loads(tar.extractfile('RESULT.json').read())if'RESULT.json'in names else None
  return summary,union,data

preliminary=[];union=set()
for folder in ['product-mask-filter-20261016','product-filter-cost-20261016','product-fused-filter-20261016','product-early-filter-20261016','product-early-cost-20261016']:
 summary,nonces,_=archive_review(folder);preliminary.append(summary);union.update(nonces)
assert union==set(range(1,262145))
attempts=sum(x['complete_nonce_row_attempts']for x in preliminary)
accounting={'status':'VERIFIED_PRELAUNCH_COMPLETE_NONCE_ROW_ACCOUNTING',
 'archives':preliminary,'preliminary_unique_nonce_range':[1,262144],'preliminary_distinct_nonces':len(union),
 'preliminary_complete_nonce_row_attempts':attempts,'preliminary_repeated_rows_within_preliminary':attempts-len(union),
 'all_preliminary_nonce_rows_repeated_in_operational_run':True,'operational_unique_completed_rows':prefix,
 'combined_distinct_nonces':prefix,'combined_operational_plus_preliminary_row_attempts':prefix+attempts,
 'scope':'All complete nonce packet JSONL rows in the five archived prelaunch candidate25 integration/control/timing experiments. In-process scalar, protected-seed, helper, per-shot and MR-control evaluations are not extra nonce packet rows. Later concurrent disabled runtime experiments are outside this explicitly prelaunch ledger. No repeats are added to the operational unique count.'}
(R/'PRELIMINARY-ATTEMPT-ACCOUNTING.json').write_text(json.dumps(accounting,indent=2)+'\n')

cost,_,costrows=archive_review('repair67-persistent-cost-20261016','95a3659f6e29b68a1c51a23f0e44e3432c9c62262447a009f98a9b001cd73ddb')
pilot,_,pilotrows=archive_review('plain67-persistent-pilot-20261016','28495fad94ee52e130df1acc0023fc62f2df979c2167b3e6430aa06e684d3eb2')
assert cost['verified_members']==83 and pilot['verified_members']==48
assert cost['complete_nonce_row_attempts']==262144 and pilot['complete_nonce_row_attempts']==65558
for dataset in [costrows,pilotrows]:
 trial_reference=None;files=0
 for name,body in dataset.items():
  if not name.startswith('trial'):continue
  parsed=sorted(map(json.loads,body.splitlines()),key=lambda row:row['nonce'])
  assert [row['nonce']for row in parsed]==list(range(1,16385))
  assert all(row['proof_accepted']is False and row['authoritative_rejection']is False for row in parsed)
  if trial_reference is None:trial_reference=parsed
  else:assert parsed==trial_reference,name
  files+=1
 assert files in [4,16]
for folder,summary in [('repair67',cost),('plain67',pilot)]:
 r=summary['result'];trials=[x for x in r['trials']if x.get('name','').startswith('trial')or'trial'in x]
 for item in trials:
  n=65536 if folder=='repair67' else 32768
  seconds=item['group_elapsed_seconds_including_startup'];workers=8 if folder=='repair67' else 4
  expected=r['expected_nonces_model']if folder=='plain67' else 181165677.0769668
  hours=expected/(n/seconds)/3600/(64/workers)
  reported=item.get('ideal_linear_64_thread_mean_hours_NOT_MEASURED',item.get('ideal_linear64_mean_model_hours_NOT_MEASURED'))
  assert math.isclose(hours,reported,rel_tol=1e-12),(folder,hours,reported)
cost_review={'status':'BOTH_PERSISTENT_COST_ARCHIVES_MANIFEST_ROW_SCOPE_AND_FORECAST_ARITHMETIC_PASS',
 'repaired67':{k:v for k,v in cost.items()if k not in('result','rowfiles')},
 'plain67':{k:v for k,v in pilot.items()if k not in('result','rowfiles')},
 'meaning':'Repaired67 uses changed A29 arithmetic plus conditional G and eight measured worker threads; plain67 uses original4b function and four measured worker threads. They have different own census models and co-tenancy. No causal throughput ranking or measured64 scalability is inferred.',
 'all_complete_trial_rows_recompared_independently_across_workers_and_modes':True,
 'no_search_authority':True}
(R/'PERSISTENT-COST-CONSISTENCY.json').write_text(json.dumps(cost_review,indent=2)+'\n')
receipt={'status':'INDEPENDENT_TERMINAL_SOURCE_RECEIPT_ACCOUNTING_AND_COST_REVIEW_PASS',
 'audit_receipt_sha256':file_sha(I/'ROOT_TERMINAL_AUDIT.json'),'audit_source_sha256':audit['audit_source_sha256'],
 'review_scope':'Read exact frozen auditor source and small terminal receipts; independently reconstruct partition/cardinality/disposition arithmetic. No second read or rerun of47million operational rows. Trust is explicitly in the completed pinned root full-log audit plus previously accepted source-bound value certificate/runtime.',
 'lowest_pass':47449113,'operational_unique_nonces':prefix,'overrun':3047,'workers_all_clean_terminal':True,
 'protected9024_pass_required_by_auditor':True,'runtime_and_auxiliary_artifact_hashes_match_acceptance':True,
 'preliminary_attempt_accounting_sha256':file_sha(R/'PRELIMINARY-ATTEMPT-ACCOUNTING.json'),
 'persistent_cost_review_sha256':file_sha(R/'PERSISTENT-COST-CONSISTENCY.json'),
 'material_findings':[],
 'disclosure_correction':'262144 preliminary distinct nonces is not the number of preliminary attempts: both262144 cost runs and all smaller prelaunch JSONL controls must be disclosed as repetitions.',
 'official_benchmark_and_final_predeclared_census_still_required':True,'score':None,'submission_mode':'queue'}
(R/'INDEPENDENT-REVIEW.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'review':receipt,'preliminary_attempts':attempts,'combined_attempts':prefix+attempts,'preliminary_per_archive':{x['folder']:x['complete_nonce_row_attempts']for x in preliminary}},indent=2))
