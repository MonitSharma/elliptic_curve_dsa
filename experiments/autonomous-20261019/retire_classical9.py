"""Publish a finite boundary stop, preserving every in-flight possible pass."""
import datetime,hashlib,json,os,signal,socket,subprocess,time
from pathlib import Path
ws=Path(__file__).resolve().parent.parent;old=ws/'product-classical-nine-operational-20261019';new=ws/'product-classical-twelve-operational-20261019';r=ws/'classical9-retirement-20261020'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
assert socket.gethostname()=='LHC-104-070' and not r.exists();r.mkdir()
assert (new/'prepare.exit').read_text().strip()=='0' and (new/'control.exit').read_text().strip()=='0'
acc=json.loads((new/'ACCEPTANCE.json').read_text());assert acc['failure_gate_pass'] and acc['cost_gate_pass']
assert sha(new/'ACCEPTANCE.json')=='5c25049df477ecd3bfa82e6059866dfda211af5085d1944e01ffabd48b93d5ff'
assert all(sha(Path(p))==h for p,h in acc['runtime_artifacts'].items())
assert json.loads((ws/'classical12-final-20261020/PATH-CONTROL.json').read_text())['status']=='CLASSICAL12_FINALIZER_ALL_INPUT_PATHS_AND_HASHES_PASS'
watch=int((ws/'classical12-final-20261020/watch.pid').read_text());assert Path(f'/proc/{watch}/cwd').resolve()==ws/'classical12-final-20261020'
assert not (old/'search.exit').exists() and not (old/'stop-after-nonce.txt').exists()
assert not list((old/'passes').glob('pass-*.json'))
profile=json.loads(subprocess.check_output(['python3',str(ws/'autonomous-20261019/preflight_v15.py')],env=dict(os.environ,RESEARCH_SLOTS='1'),text=True))
(r/'preflight.json').write_text(json.dumps(profile,indent=2)+'\n')
pids=[];parents=set()
for lane in range(4):
 pid=int((old/f'worker{lane}.pid').read_text());assert Path(f'/proc/{pid}/cwd').resolve()==old
 assert Path(f'/proc/{pid}/exe').resolve()==old/'tool/target/release/value_prefilter'
 status=Path(f'/proc/{pid}/status').read_text();assert not '\nState:\tZ' in status
 parents.add(int(next(s.split()[1] for s in status.splitlines() if s.startswith('PPid:'))));pids.append(pid)
assert len(parents)==1;manager=parents.pop()
assert Path(f'/proc/{manager}/cwd').resolve()==old and b'coordinator.py' in Path(f'/proc/{manager}/cmdline').read_bytes().split(b'\0')
assert sha(old/'tool/target/release/value_prefilter')=='e6971995f1d56d1bb3011eee74efed437ad01f4540d8acaebc066da5f7b34d9d'
frozen=[]
try:
 for pid in [manager,*pids]:os.kill(pid,signal.SIGSTOP);frozen.append(pid)
 deadline=time.monotonic()+5
 while not all(next(s.split()[1] for s in Path(f'/proc/{p}/status').read_text().splitlines() if s.startswith('State:'))=='T' for p in frozen):
  assert time.monotonic()<deadline;time.sleep(.01)
 assert not list((old/'passes').glob('pass-*.json')),'A pass arrived; resume and let existing finalizer resolve it'
 rows=[json.loads((old/f'worker{lane}-progress.json').read_text()) for lane in range(4)]
 for lane,row in enumerate(rows):assert row['lane']==lane and row['count']==4096 and row['status']=='COMPLETE_WINDOW_ALL_ROWS_RECORDED'
 # Each lane has at most one current window, at most 16384 beyond its last completed window.
 # Two complete global cycles above max completed last cover every possible in-flight pass.
 cutoff=(max(x['last'] for x in rows)//16384+2)*16384
 tmp=r/'finite-stop.txt'
 with tmp.open('x') as f:f.write(str(cutoff)+'\n');f.flush();os.fsync(f.fileno())
 os.link(tmp,old/'stop-after-nonce.txt')
 receipt={'status':'FINITE_BETWEEN_WINDOW_STOP_REQUESTED','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'reason':'A genuinely lower-T finished source passed its own gate and runtime controls; replace only if old search terminates without a pass.',
 'cutoff':cutoff,'stable_progress':rows,'worker_pids':pids,'coordinator_pid':manager,
 'new_acceptance_sha256':sha(new/'ACCEPTANCE.json'),'new_control_sha256':sha(new/'CONTROL.json'),
 'scope':'Only these own research processes paused briefly and resumed; chemistry untouched. Every in-flight pass lies below finite cutoff. All logs/source retained. Any arriving pass goes to existing lowest-prefix auditor.'}
 (r/'REQUEST.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
finally:
 for pid in reversed(frozen):os.kill(pid,signal.SIGCONT)
