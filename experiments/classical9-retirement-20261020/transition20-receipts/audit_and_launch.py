import datetime,hashlib,json,os,shutil,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;old=ws/'product-classical-nine-operational-20261019'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
assert not (r/'TERMINAL.json').exists()
while not (old/'search.exit').exists():time.sleep(5)
t=json.loads((old/'RESULT.json').read_text())
assert (old/'search.exit').read_text().strip()=='0' and t['worker_exit_codes']==[0]*4
if t['best_full_protected_pass'] is not None or list((old/'passes').glob('pass-*.json')):
 (r/'PASS-PRESERVED.json').write_text(json.dumps({'status':'PASS_ARRIVED_OLD_FINALIZER_MUST_RESOLVE','terminal':t},indent=2)+'\n');raise SystemExit(2)
auditor=ws/'classical9-final-v3-20261020/audit-terminal.py'
assert sha(auditor)=='47e8c89c308a15026a4da85310829f8a35188149716fcc6fb349adcac5d27ba1'
profile=json.loads(subprocess.check_output(['python3',str(ws/'autonomous-20261019/preflight_v15.py')],env=dict(os.environ,RESEARCH_SLOTS='1'),text=True))
(r/'audit-preflight.json').write_text(json.dumps(profile,indent=2)+'\n')
with (r/'complete-audit.log').open('xb') as f:subprocess.run(['python3',str(auditor),str(old),str(r/'COMPLETE-LOG-AUDIT.json')],stdout=f,stderr=subprocess.STDOUT,check=True)
a=json.loads((r/'COMPLETE-LOG-AUDIT.json').read_text());assert a['status']=='NO_PASS_COMPLETE_JSONL_AUDIT_PASS' and a['lowest_full_protected_pass'] is None
assert a['complete_global_prefix']==a['operational_unique_nonces']==json.loads((r/'REQUEST.json').read_text())['cutoff']
receipts=r/'terminal-receipts';receipts.mkdir()
for name in ['RESULT.json','search.exit','run-record.json','search-preflight.json','SEARCH_SOURCE.sha256','stop-after-nonce.txt']+[f'worker{i}{suffix}' for i in range(4) for suffix in ['.pid','.exit','-progress.json']]:shutil.copy2(old/name,receipts/name)
for _ in range(12):
 if (ws/'classical9-final-v3-20261020/WATCH_RESULT.json').exists():break
 time.sleep(5)
watch=json.loads((ws/'classical9-final-v3-20261020/WATCH_RESULT.json').read_text());assert watch['status']=='NO_FINALIZATION'
terminal={'status':'RETIRED_NO_PASS_ALL_TERMINAL_ROWS_INDEPENDENTLY_AUDITED','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'old_terminal':t,'complete_jsonl_audit_sha256':sha(r/'COMPLETE-LOG-AUDIT.json'),'auditor_sha256':sha(auditor),'complete_global_prefix':a['complete_global_prefix'],'files_retained_on_server':[str(old/f'worker{i}.jsonl') for i in range(4)],'watcher_terminal':watch,'replacement_from_nonce':1,'no_scored_result':True}
(r/'TERMINAL.json').write_text(json.dumps(terminal,indent=2)+'\n');print(json.dumps(terminal,indent=2),flush=True)
subprocess.run(['python3',str(ws/'product-classical-twelve-operational-20261019/launch_search.py')],check=True)
