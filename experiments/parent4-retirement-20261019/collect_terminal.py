import datetime,hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'parent4-operational-sat-20261019'
assert (old/'search.exit').read_text().strip()=='0' and not (r/'TERMINAL.json').exists()
terminal=json.loads((old/'RESULT.json').read_text());assert terminal['worker_exit_codes']==[0]*4
assert terminal['best_full_protected_pass'] is None and not list((old/'passes').glob('pass-*.json')),'Resolve any preserved pass rather than discarding it'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
files={}
for name in ['RESULT.json','run-record.json','ACCEPTANCE.json','CONTROL.json','search.exit','SEARCH-SOURCE.sha256']+[f'worker{i}{suffix}' for i in range(4) for suffix in ['.jsonl','.log','.err','.exit','-progress.json']]:
    p=old/name;before=p.stat();digest=sha(p);after=p.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
    files[name]={'bytes':after.st_size,'sha256':digest}
result={'status':'OLD_SOURCE_STOPPED_CLEANLY_NO_PASS_ALL_LOGS_PRESERVED','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'terminal':terminal,'files':files,
 'scope':'Controller-reported completed rows and exact immutable file hashes. Full JSONL coverage audit is not claimed; no old nonce is selected. No old source/proof/runtime path is deleted.'}
(r/'TERMINAL.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'reported_completed_rows':terminal['screened_unique_completed_rows'],'files_hashed':len(files)},indent=2))
