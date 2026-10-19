"""One disabled validation only after this exact source's sole final gate passes."""
import hashlib,json,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent;n=r.parent/'product-copy-cache-native-20261020'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
bound=json.loads((r/'WATCH_SOURCE.json').read_text())
assert not (r/'WATCH_RESULT.json').exists()
while not (r/'build.exit').exists() or not (n/'gate.exit').exists():time.sleep(15)
assert all(sha(r/p)==h for p,h in bound.items())
gate=json.loads((n/'qualification/RESULT.json').read_text()) if (n/'qualification/RESULT.json').exists() else None
if (r/'build.exit').read_text().strip()!='0' or (n/'gate.exit').read_text().strip()!='0' or not gate or gate['status']!='FAILURE_GATE_PASS' or not all(gate['rules'].values()):
    (r/'WATCH_RESULT.json').write_text(json.dumps({'status':'DISABLED_QUALIFICATION_REFUSED_BUILD_OR_FINAL_GATE','at_utc':datetime.now(timezone.utc).isoformat(),'build_exit':(r/'build.exit').read_text().strip(),'gate_exit':(n/'gate.exit').read_text().strip(),'gate_status':gate['status'] if gate else None,'new_source_nonce_tests_started':False,'verdict_is_final_no_rerun':True},indent=2)+'\n');raise SystemExit(0)
def manager_live(root,pidfile):
    pid=int((root/pidfile).read_text());p=Path('/proc')/str(pid)
    if not (p/'status').exists():return False
    state=next(x.split()[1] for x in (p/'status').read_text().splitlines() if x.startswith('State:'))
    return state!='Z' and (p/'cwd').resolve()==root
while manager_live(n,'gate.pid') or manager_live(r,'build.pid'):time.sleep(1)
assert not (r/'qualification.pid').exists() and not (r/'QUALIFICATION-START.json').exists()
with (r/'qualification-nohup.log').open('xb') as f:
    p=subprocess.Popen(['nohup','bash','run-qualify.sh'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
    (r/'qualification.pid').write_text(str(p.pid)+'\n');code=p.wait()
(r/'WATCH_RESULT.json').write_text(json.dumps({'status':'DISABLED_RUNTIME_QUALIFICATION_FINISHED','qualification_exit':code,'at_utc':datetime.now(timezone.utc).isoformat(),'authoritative_rejection':False,'nonce_selected':None,'production_changed':False},indent=2)+'\n')
raise SystemExit(code)
