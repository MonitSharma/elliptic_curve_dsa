"""Persistent queue-only audit/benchmark after the existing search ends."""
import datetime,hashlib,json,os,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;s=r.parent/'parent4-operational-sat-20261019'
def save(name,value): (r/name).write_text(json.dumps(value,indent=2)+'\n')
def log(message):
    with (r/'watch.log').open('a') as f:f.write(datetime.datetime.now(datetime.timezone.utc).isoformat()+' '+message+'\n')
assert not (r/'WATCH_RESULT.json').exists()
bound={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in r.iterdir() if p.suffix in {'.py','.sh'}}
save('WATCH_SOURCE.json',bound)
log('Waiting for terminal search; queue mode, no upload')
while not (s/'search.exit').exists():time.sleep(30)
assert all(hashlib.sha256((r/p).read_bytes()).hexdigest()==h for p,h in bound.items())
terminal=json.loads((s/'RESULT.json').read_text())
if (s/'search.exit').read_text().strip()!='0' or terminal['status']!='PASS_AWAITS_COMPLETE_LOG_AUDIT_AND_UNCHANGED_BENCHMARK':
    save('WATCH_RESULT.json',{'status':'NO_FINALIZATION','search':terminal,'submission_mode':'queue'});log('Search ended without certifiable pass');raise SystemExit(0)
with (r/'terminal-audit.log').open('wb') as f:
    audit=subprocess.run(['python3',str(r/'audit-terminal.py'),str(s),str(r/'ROOT_TERMINAL_AUDIT.json')],stdout=f,stderr=subprocess.STDOUT)
if audit.returncode:
    save('WATCH_RESULT.json',{'status':'TERMINAL_AUDIT_FAILED','audit_exit':audit.returncode});raise SystemExit(audit.returncode)
log('Complete lower-prefix audit passed; launching unchanged native benchmark')
with (r/'final.nohup.log').open('wb') as f:
    p=subprocess.Popen(['nohup','bash','run-final.sh'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
    (r/'final.pid').write_text(str(p.pid)+'\n');code=p.wait()
b=r/'BENCHMARK_RESULT.json';result=json.loads(b.read_text()) if b.exists() else None
save('WATCH_RESULT.json',{'status':'READY_FOR_EVIDENCE_REVIEW' if code==0 and result and result.get('beats_public_product_record') else 'FINALIZATION_INCOMPLETE_OR_NOT_A_RECORD',
    'run_final_exit':code,'benchmark':result,'submission_mode':'queue','no_later_nonce_search_for_score':True})
log('Finalization ended; exit '+str(code))
