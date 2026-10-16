from pathlib import Path
import hashlib,json,re,subprocess,datetime,shutil
r=Path(__file__).resolve().parent; root=r.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
groups={628797:'PRODUCT25 final native/benchmark coordinator',595517:'ALL70 fixed67 cache chain',
        595518:'ALL70 native watcher',595519:'ALL70 census watcher',606954:'ALL70 terminal archive watcher'}
rows=subprocess.check_output(['ps','-eo','pid,ppid,pgid,sid,stat,args'],text=True).splitlines()
owned=[]
for line in rows[1:]:
    a=line.split(None,5)
    if len(a)>=6 and int(a[2]) in groups:
        assert a[4].startswith('T'),line
        owned.append(dict(pid=int(a[0]),ppid=int(a[1]),pgid=int(a[2]),sid=int(a[3]),state=a[4],command=a[5]))
assert set(x['pgid'] for x in owned)==set(groups)
log=(r/'benchmark.log').read_text(); score=json.loads((r/'candidate/score.json').read_text())
for label,expected in [('tested shots',9024),('classical mismatches',0),('phase-garbage batches',0),('ancilla-garbage batches',0)]:
    assert re.findall(re.escape(label)+r'\s*:\s*(\d+)',log)==[str(expected)]
assert 'all 9024 shots OK' in log and '=== experiment OK ===' in log
total=int(re.search(r'total Toffoli \(sum\)\s*:\s*(\d+) over 9024 shots',log).group(1))
freeze=json.loads((r/'SOURCE_FREEZE.json').read_text())
point_add={p:sha(r/'candidate'/p) for p in freeze['source_files']}
assert point_add==freeze['source_files']
protected={p:sha(r/'candidate'/p) for p in freeze['protected_files']}
changed=[p for p in protected if protected[p]!=freeze['protected_files'][p]]
assert set(changed)<= {'results.tsv'}
old=subprocess.check_output(['git','-C',str(r/'candidate'),'show','HEAD:results.tsv'])
generated=(r/'candidate/results.tsv').read_bytes();assert generated.startswith(old)
delta=generated[len(old):]; assert len(delta.decode().splitlines())==1
assert delta.decode().split('\t')[6]=='OK'
saved=r/'stop-preserved';saved.mkdir(exist_ok=True)
for source,name in [(r/'candidate/results.tsv','generated-full-results.tsv'),(r/'candidate/score.json','score.json'),
                    (r/'benchmark.log','benchmark.log')]:shutil.copy2(source,saved/name)
(saved/'appended-results-row.tsv').write_bytes(delta)
stream=sha(r/'candidate/ops.bin');assert stream=='93122ce2668fe2861eba894b1520d3e44552c2094487337dd92300c2aa9d57d2'
chain=root/'product-exact-20261015/all70-cache67-20261016'
receipts=json.loads((chain/'CACHE_STAGE_RECEIPTS.json').read_text())
# Count only terminal UNIVERSAL_PASS JSON rows, never the interrupted audit.
complete=[json.loads(x) for x in (chain/'cache-chain.log').read_text().splitlines() if x.strip()]
assert complete[-1]['stage']==19 and complete[-1]['status']=='UNIVERSAL_PASS'
x={'status':'USER_REQUESTED_REVERSIBLE_STOP_NO_NEW_WORK','time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
   'stopped_groups':groups,'process_snapshot':owned,'no_processes_killed':True,'no_submission':True,
   'product25':{'status':'UNCHANGED_BENCHMARK_COMPLETE_PASS_POSTVERIFIER_PAUSED_FINAL_FRESH_CENSUS_NOT_RUN',
     'candidate':str(r/'candidate'),'nonce':47449113,'score':score,'shots':9024,
     'classical_mismatches':0,'phase_garbage_batches':0,'ancilla_garbage_batches':0,
     'total_executed_toffoli':total,'mean_executed_toffoli':total/9024,
     'old_public_product':939347948,'product_improvement':939347948-score['score'],
     'stream_sha256':stream,'source_freeze_sha256':sha(r/'SOURCE_FREEZE.json'),
     'native_receipt_sha256':sha(r/'NATIVE_RECEIPT.json'),'all_point_add_sources_still_frozen':True,
     'protected_file_changes':changed,'protected_results_exception':'Exactly one unchanged-scorer OK row appended; copied with delta; candidate file remains untouched while paused',
     'benchmark_result_json_present':(r/'BENCHMARK_RESULT.json').exists(),'final_exit_present':(r/'final.exit').exists(),
     'final_census_plan':str(r/'FINAL-CENSUS-PLAN.json'),'final_fresh_census_launched':False,
     'submission_readiness':'Not yet complete under predeclared finalfresh requirement; no submission'},
   'all70':{'last_complete_universal_stage':19,'paused_stage':20,'fixed_endpoint':67,
      'last_complete_stream':complete[-1]['output_stream'],'last_complete_sha256':complete[-1]['output_sha256'],
      'final_native_and_census_not_started':True,'no_partial_checkpoint_submission_authority':True},
   'wide4096_record':{'status':'DECLARATION_ONLY_NO_SOURCE_COPY_SEARCH_BUILD_OR_BENCHMARK_LAUNCHED',
      'declaration':str(root/'wide15-retained4096-record-20261016/DECLARATION.json'),
      'declaration_sha256':sha(root/'wide15-retained4096-record-20261016/DECLARATION.json')},
   'preserved_files':{str(p.relative_to(r)):sha(p) for p in sorted(saved.iterdir()) if p.is_file()},
   'resume_requires':'Explicit user authorization; recheck exact leader commands/PGIDs and resources; SIGCONT selected owned group only. No automatic resume. Parent also paused its own census coordinator.'}
(r/'STOP-CHECKPOINT.json').write_text(json.dumps(x,indent=2)+'\n')
text=f'''All owned work was reversibly paused at the user's request. No process was killed, no new workload was launched, and no submission was made.

PRODUCT25's unchanged benchmark completed before the stop: all9,024shots passed with classical0, phase0, ancilla0. Its authoritative score is Q1234, roundedT761171, product939285014, improving the current939347948 product by62,934. Exact executedT total is{total}, mean{total/9024:.12f}. Nonce47,449,113 is the audited lowest passing operational nonce. The regenerated stream still has SHA256{stream}, identical to the previously verified native selected stream. Every point_add file remains frozen.

The post-benchmark verifier is paused before its final receipt. The scorer appended exactly one OK row to tracked results.tsv; the full file and delta, score and complete benchmark log are copied under stop-preserved/. The candidate's generated results file has deliberately not been altered during the pause. The final predeclared32768-batch fresh census has NOT run. Therefore this is a passing benchmark candidate with final qualification still pending, not a completed submission-ready record.

Stopped process groups:628797(PRODUCT25 final);595517(ALL70 cache chain);595518(ALL70 native watcher);595519(ALL70 census watcher);606954(ALL70 terminal archive watcher). Every observed process in these groups is in stateT. Full PIDs, commands and states are in STOP-CHECKPOINT.json.

ALL70 has19 complete universally checked stages. Stage20's universal audit is paused; its fixed endpoint remains67. Native final generation and final census have not started. No intermediate checkpoint has submission authority.

The separate wide15-retained4096-record directory contains only the protocol declared before search. No search, source copy, build, new benchmark or final census was launched for it. The root-owned frozen probe and its prior passing gate remain preserved separately.

Resumption requires explicit user authorization and fresh verification of leader commands, process groups and resources. Resume only the desired owned group with SIGCONT; waiting native/census/archive groups would otherwise launch future phases once their conditions are met. Nothing is set to resume automatically.
'''
(r/'STOP-CHECKPOINT.md').write_text(text)
print(json.dumps(x,indent=2))
