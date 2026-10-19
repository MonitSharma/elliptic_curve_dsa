"""Independently audit and package a complete passing native result; never upload."""
import hashlib,io,json,math,subprocess,tarfile,time,urllib.request
from datetime import datetime,timezone
from pathlib import Path
ws=Path(__file__).resolve().parent.parent;r=ws/'classical12-final-20261020';t=r/'candidate';s=ws/'product-classical-twelve-operational-20261019';n=ws/'product-classical-twelve-native-20261019'
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
save=lambda name,value:(r/name).write_text(json.dumps(value,indent=2)+'\n')
assert (r/'final.exit').read_text().strip()=='0' and read(r/'WATCH_RESULT.json')['status']=='READY_FOR_EVIDENCE_REVIEW'
assert not (r/'INDEPENDENT-FINAL-AUDIT.json').exists(),'Never silently overwrite a final review'
bench=read(r/'BENCHMARK_RESULT.json');score=read(r/'score.json');freeze=read(r/'SOURCE_FREEZE.json');native=read(r/'NATIVE_RECEIPT.json');audit=read(r/'ROOT_TERMINAL_AUDIT.json');terminal=read(s/'RESULT.json');gate=read(n/'qualification/RESULT.json');decl=read(n/'qualification/DECLARATION.json')
assert bench['status']=='UNCHANGED_BENCHMARK_PASS' and bench['beats_public_product_record']
assert bench['tested_shots']==9024 and all(bench[k]==0 for k in ['classical_mismatches','phase_garbage_batches','ancilla_garbage_batches'])
q,tof=score['metrics']['qubits'],score['metrics']['toffoli'];product=q*tof
assert q==1234 and product==score['score']==bench['product'] and tof==bench['rounded_mean_toffoli']
assert math.floor(bench['total_executed_toffoli']/9024+.5)==tof and bench['mean_executed_toffoli']==bench['total_executed_toffoli']/9024
assert sha(r/'benchmark.log')==bench['benchmark_log_sha256'] and sha(r/'score.json')==bench['score_sha256']
log=(r/'benchmark.log').read_text();assert 'all 9024 shots OK' in log and '=== experiment OK ===' in log
assert (t/'results.tsv').read_bytes()==subprocess.check_output(['git','-C',str(t),'show','HEAD:results.tsv'])
assert len(freeze['source_files'])==180 and len(freeze['protected_files'])==17
assert all(sha(t/p)==h for p,h in {**freeze['source_files'],**freeze['protected_files']}.items())
assert {p.relative_to(t).as_posix() for p in (t/'src/point_add').rglob('*') if p.is_file()}==set(freeze['source_files'])
assert sha(r/'point-add-source.tar.gz')==freeze['selected_source_archive_sha256'] and sha(r/'candidate-source.patch')==freeze['patch_sha256']
with tarfile.open(r/'point-add-source.tar.gz') as a:
 assert {m.name for m in a.getmembers() if m.isfile()}==set(freeze['source_files'])
 for name,h in freeze['source_files'].items():assert hashlib.sha256(a.extractfile(name).read()).hexdigest()==h
assert native['status']=='NATIVE_SELECTED_NONCE_PREFIX_AND_TAIL_PASS' and native['pre_tail_byte_identical'] and native['tail_is_48_unconditional_xx_pairs']
assert sha(t/'ops.bin')==native['candidate_stream_sha256']==bench['candidate_stream_sha256']
assert sha(r/'SOURCE_FREEZE.json')==native['source_freeze_sha256']
assert sha(r/'audit-terminal.py')=='c95db4102bbd6a313ec3abcd72916edf54950501cc3c9a518aea7ca65fb984a0'
assert (s/'search.exit').read_text().strip()=='0' and terminal['worker_exit_codes']==[0]*4
assert audit['status']=='LOWEST_PASS_COMPLETE_JSONL_AUDIT_PASS' and audit['complete_global_prefix']>=freeze['nonce']==native['tail_nonce']==bench['nonce']==audit['lowest_full_protected_pass']==terminal['best_full_protected_pass']
assert audit['operational_unique_nonces']==terminal['screened_unique_completed_rows']==sum(lane['rows'] for lane in audit['lanes'])
for lane in audit['lanes']:
 p=s/f"worker{lane['lane']}.jsonl";assert p.stat().st_size==lane['bytes'] and sha(p)==lane['sha256']
assert all(sha(Path(p))==h for p,h in audit['runtime_artifacts_rehashed'].items())
assert read(r/'TAILCHECK.json')['status']=='TAIL_INVARIANCE_PASS' and read(r/'TAILCHECK.json')['batches']==512
assert gate['status']=='FAILURE_GATE_PASS' and all(gate['rules'].values()) and gate['label']==decl['label']=='pareto-parent4-classical12-gate-20261019-v1'
assert gate['batches']==decl['batch_count']==262144 and decl['shots_per_batch']==64
assert gate['value_shots']['candidate']<=gate['value_shots']['parent'] and gate['dirty_shots']['candidate']==0
assert 141*gate['failed_batches']['candidate']<=18*gate['batches']
b,c=gate['newly_failing_b'],gate['newly_passing_c'];total=b+c
term=math.comb(total,b);numerator=term
for k in range(b,total):term=term*(total-k)//(k+1);numerator+=term
p=numerator/2**total;assert p>=.05 and p==gate['mcnemar_one_sided_p']
counts={}
for key in ['parent','candidate']:
 path=n/'qualification'/(key+'.jsonl');assert sha(path)==gate['census_sha256'][key]
 out={'batches':0,'shots':0,'failed_batches':0,'failed_shots':0,'value_shots':0,'phase_shots':0,'dirty_shots':0,'phase_only_shots':0}
 with path.open() as f:
  for line in f:
   row=json.loads(line);assert row['batch']==out['batches'] and row['shots']==64 and row.get('skipped',0)==0
   out['batches']+=1;out['shots']+=64;out['failed_batches']+=bool(row['failures']);out['failed_shots']+=len(row['failures'])
   for field in ['value_shots','phase_shots','dirty_shots']:out[field]+=row[field]
   out['phase_only_shots']+=sum(bool(x['phase']) and not x['value'] and not x['dirty'] for x in row['failures'])
 assert out['batches']==gate['batches'] and out['failed_batches']==gate['failed_batches'][key] and out['value_shots']==gate['value_shots'][key] and out['dirty_shots']==gate['dirty_shots'][key]
 out['failed_batches_per_9024_packet']=141*out['failed_batches']/out['batches'];out['value_shot_failure_rate']=out['value_shots']/out['shots'];out['phase_shot_failure_rate']=out['phase_shots']/out['shots']
 counts[key]=out
save('DISCLOSED-CENSUS-COUNTS.json',{'label':gate['label'],'existing_rows_only':True,'counts':counts,'b':b,'c':c,'exact_mcnemar_p':p,'no_new_census_or_verdict_change':True})
api='https://api.ecdsa.fail/api/benchmarks/1ffb695a-309b-46b6-a728-2f97d8c7be74'
for name,url in [('public-final-submissions.json',api+'/submissions'),('public-final-benchmark.json',api)]:
 for attempt in range(3):
  try:data=urllib.request.urlopen(url,timeout=45).read();break
  except Exception:
   if attempt==2:raise
   time.sleep(2)
 (r/name).write_bytes(data)
rows=read(r/'public-final-submissions.json')['submissions']
eligible=[x for x in rows if (x.get('status')=='accepted' or (x.get('status')=='rejected' and x.get('rejectionReason')=='score did not improve current best')) and type(x.get('officialScore')) is int and x['officialScore']>0 and x['officialScore']==(x.get('officialMetrics')or{}).get('qubits',0)*(x.get('officialMetrics')or{}).get('toffoli',0)]
leader=min(eligible,key=lambda x:x['officialScore']);assert leader['id']=='9dc3798c-93e0-4da4-a6a9-37586737c4af' and product<leader['officialScore'],'Require current exact public-parent qualification and a complete product improvement'
public={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'leader':leader,'raw_sha256':{name:sha(r/name) for name in ['public-final-submissions.json','public-final-benchmark.json']}}
save('PUBLIC-FINAL-CHECK.json',public)
gain=leader['officialScore']-product
note=f'''# Queued exact classical-factor point-addition optimization

Complete unchanged native benchmark PASS: Q={q}, rounded mean executed
Toffolis={tof}, product={product}. Total executed T={bench['total_executed_toffoli']}
over9024 protected shots; mean={bench['mean_executed_toffoli']:.12f}. Zero
classical mismatches, phase-garbage batches or dirty-ancilla batches.
Fresh public product parent9dc3798c remains {leader['officialScore']}; local
complete-product improvement={gain} ({100*gain/leader['officialScore']:.8f}%).
This is a locally passing reproduction, not an official submission/evaluation.

Frozen native source: base0c3a0751ab66bd9144358d67563bcb79201cf636,
180 src/point_add files; all17 protected tracked files unchanged. Existing
public approximate arithmetic and tables/cuts retained; new exact identities
do not establish all-input arithmetic correctness. All earlier failed gates,
including Product25, retain their verdicts. Attribution and parent history
remain in the preserved original source and repository research records.

Source was finished before any source12 nonce evaluation. Only the identity
tail literal changed from1048009047001 to{freeze['nonce']}. Native pre-tail
bytes match exactly (SHA3-256 {native['pre_tail_sha3_256']});48 unconditional
XX pairs encode the nonce. No circuit/table/cut tuning to a packet and no
nonce selection by Toffoli score.

Nonce={freeze['nonce']}, the lowest full protected pass after complete JSONL
accounting from1. Production screened{audit['operational_unique_nonces']} unique
nonces, including{audit['operational_overrun_above_lowest']} parallel-overrun rows
above the lowest pass. Every nonce below it is covered, with complete global
prefix{audit['complete_global_prefix']}. All4 workers exited0. Preliminary
disabled-runtime/control qualification recorded28950 repeated row attempts
over unique1..4096; production repeats from1. Own-seed byte references1,2,17,255
and nonce1 full-state references are separate checks. These repeated/reference
checks are not added to the production unique count. Full terminal logs remain
on the server, with every byte bound by the complete audit and independent
rehashing; parent4/source9 searches are separate frozen circuits and do not
justify this circuit's lower-prefix coverage.

Sole final statistical gate, declared before runs:
{gate['label']},262144 batches x64 shots=16777216 shots PER source, against
the exact public9dc stream on the same fresh inputs. Value-failing shots:
candidate{gate['value_shots']['candidate']},parent{gate['value_shots']['parent']}.
Failed batches: candidate{gate['failed_batches']['candidate']},parent{gate['failed_batches']['parent']}.
Candidate failed batches per9024-shot packet={gate['failed_batches_per_packet']['candidate']}.
Paired newly failing b={b},newly passing c={c}; one-sided exact McNemar p={p}.
Zero dirty shots. Phase and failing-shot rates are fully disclosed in
DISCLOSED-CENSUS-COUNTS.json. All4 rules PASS; this verdict was never relabelled,
extended, rerun or rejudged. Full original census rows/archive are preserved.
The512-batch selected-tail control reuses the existing gate inputs and matches
every original row; it is an invariance control, not a second statistical gate.

Selected native stream SHA256 {native['candidate_stream_sha256']}.
Selected source archive SHA256 {freeze['selected_source_archive_sha256']}.
Patch SHA256 {freeze['patch_sha256']}.
Failure-gate result SHA256 {sha(n/'qualification/RESULT.json')}.
Complete nonce-audit SHA256 {sha(r/'ROOT_TERMINAL_AUDIT.json')}.
Benchmark log SHA256 {sha(r/'benchmark.log')}.

Queue mode only. No uploader invoked. Review source/evidence before any
separately authorized official submission; refresh public records again then.
'''
(r/'SUBMISSION-NOTE.md').write_text(note)
review={'status':'ALL_FINAL_REQUIREMENTS_INDEPENDENTLY_VERIFIED_COMPLETE_LOCAL_PRODUCT_IMPROVEMENT','at_utc':datetime.now(timezone.utc).isoformat(),'nonce':freeze['nonce'],'qubits':q,'rounded_mean_executed_toffoli':tof,'product':product,'public_product':leader['officialScore'],'product_improvement':gain,'source_files':180,'protected_files_unchanged':17,'native_pre_tail_identical':True,'gate_rules_pass':True,'gate_label':gate['label'],'lowest_pass_complete_audit':True,'production_unique_screened':audit['operational_unique_nonces'],'unchanged_benchmark_shots':9024,'benchmark_failures':0,'historical_results_restored':True,'submission_mode':'queue','uploaded':False,'script_sha256':sha(Path(__file__))}
save('INDEPENDENT-FINAL-AUDIT.json',review)
files={};paths={}
for path in sorted(r.iterdir()):
 if not path.is_file() or path.name.startswith(('cycle20','review-source','final-evidence','FINAL-EVIDENCE')) or path.suffix=='.bin':continue
 if path.name.endswith('.tar.gz') and path.name!='point-add-source.tar.gz':continue
 if path.stat().st_size>25_000_000:continue
 paths[path.name]=path;files[path.name]={'bytes':path.stat().st_size,'sha256':sha(path)}
for key,path in {'gate/DECLARATION.json':n/'qualification/DECLARATION.json','gate/RESULT.json':n/'qualification/RESULT.json','gate/GATE-AUDIT.json':n/'GATE-AUDIT.json','search/RESULT.json':s/'RESULT.json','search/run-record.json':s/'run-record.json','search/ACCEPTANCE.json':s/'ACCEPTANCE.json'}.items():paths[key]=path;files[key]={'bytes':path.stat().st_size,'sha256':sha(path)}
manifest={'at_utc':datetime.now(timezone.utc).isoformat(),'scope':'Complete locally passing lower-product source, native benchmark, sole statistical gate and lowest-nonce evidence. Queue only; no official upload.', 'included_files':files,'full_terminal_worker_logs_retained_on_server':audit['lanes'],'server_search_directory':str(s),'complete_original_gate_archive':{'path':str(n/'gate-evidence.tar.gz'),'sha256':sha(n/'gate-evidence.tar.gz')},'selected_stream_retained_on_server':{'path':str(t/'ops.bin'),'sha256':sha(t/'ops.bin')}}
with tarfile.open(r/'final-evidence.tar.gz','x:gz') as a:
 for key,path in paths.items():a.add(path,arcname=key,recursive=False)
 raw=(json.dumps(manifest,indent=2)+'\n').encode();m=tarfile.TarInfo('SNAPSHOT-MANIFEST.json');m.size=len(raw);a.addfile(m,io.BytesIO(raw))
save('FINAL-EVIDENCE.json',{'archive':'final-evidence.tar.gz','bytes':(r/'final-evidence.tar.gz').stat().st_size,'sha256':sha(r/'final-evidence.tar.gz'),'files':len(files),'audit':review})
save('QUEUED-READY.json',{'status':'QUEUED_COMPLETE_LOCAL_PRODUCT_IMPROVEMENT','candidate_directory':str(t),'submission_note':str(r/'SUBMISSION-NOTE.md'),'evidence_sha256':sha(r/'final-evidence.tar.gz'),'metrics':review,'uploaded':False})
print(json.dumps(review,indent=2),flush=True)
