"""Replace an idle own watcher only, preserving its immutable source and receipts."""
import hashlib,json,os,signal,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
ws=Path(__file__).resolve().parent.parent;old=ws/'classical9-final-20261019';new=ws/'classical9-final-v2-20261019';search=ws/'product-classical-nine-operational-20261019'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
ready=json.loads((new/'READY.json').read_text());assert ready['status']=='COPIED_BOUND_AUDITOR_AND_ALL_NATIVE_RUNTIME_GATE_PATHS_PASS'
assert all(sha(new/p)==h for p,h in ready['source_files'].items())
assert sha(ws/'autonomous-20261019/preflight_v14.py')==ready['profile_sha256']
assert not (old/'final.pid').exists() and not (old/'WATCH_RESULT.json').exists()
assert not (search/'search.exit').exists() and not list((search/'passes').glob('pass-*.json')),'Let existing finalization finish if search has a pass'
assert not (new/'watch.pid').exists()
pid=int((old/'watch.pid').read_text());proc=Path('/proc')/str(pid)
assert (proc/'cwd').resolve()==old and (proc/'cmdline').read_bytes().split(b'\0')[1]==b'watch.py'
assert not (proc/'task'/str(pid)/'children').read_text().strip(),'Old watcher has active audit or benchmark; do not stop it'
bound=json.loads((old/'WATCH_SOURCE.json').read_text());assert all(sha(old/p)==h for p,h in bound.items())
profile=json.loads(subprocess.check_output(['python3',str(ws/'autonomous-20261019/preflight_v14.py')],env=dict(os.environ,RESEARCH_SLOTS='1'),text=True))
receipt={'at_utc':datetime.now(timezone.utc).isoformat(),'status':'PREPARED_OLD_IDLE_WATCHER_REPLACEMENT','old_pid':pid,'old_source_files_preserved':bound,'profile':profile,'circuit_changed':False,'search_changed':False,'reason':'New explicit registry permits forthcoming source12 runtime validation while retaining the entire frozen source9 search/finalization path.'}
out=ws/'autonomous-20261019/FINALIZER-V2-TRANSITION.json';assert not out.exists()
# Freeze only this verified own watcher, then recheck that it did not start an
# audit between the earlier read and the replacement. Resume it on any refusal.
stopped=False
try:
    os.kill(pid,signal.SIGSTOP);stopped=True
    for _ in range(100):
        state=next(x.split()[1] for x in (proc/'status').read_text().splitlines() if x.startswith('State:'))
        if state.startswith('T'):break
        time.sleep(.01)
    else:raise RuntimeError('Old watcher did not enter the requested idle checkpoint')
    assert not (proc/'task'/str(pid)/'children').read_text().strip(),'Resume existing audit; never replace an active coordinator'
    assert not (old/'final.pid').exists() and not (old/'WATCH_RESULT.json').exists()
    out.write_text(json.dumps(receipt,indent=2)+'\n')
    os.kill(pid,signal.SIGTERM);os.kill(pid,signal.SIGCONT);stopped=False
except BaseException:
    if stopped:os.kill(pid,signal.SIGCONT)
    raise
for _ in range(100):
    if not (proc/'status').exists() or '\nState:\tZ' in (proc/'status').read_text():break
    time.sleep(.05)
else:raise RuntimeError('Old watcher did not exit; new watcher not started')
assert all(sha(old/p)==h for p,h in bound.items())
subprocess.run(['python3',str(new/'launch_watch.py')],check=True)
newpid=int((new/'watch.pid').read_text());time.sleep(.3)
assert Path('/proc',str(newpid),'cwd').resolve()==new
receipt.update(status='OLD_IDLE_WATCHER_RETIRED_NEW_QUEUE_FINALIZER_LIVE',new_pid=newpid,old_source_unchanged=True,new_source_files=json.loads((new/'WATCH_SOURCE.json').read_text()))
out.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'status':receipt['status'],'old_pid':pid,'new_pid':newpid}))
