"""Use only the old coordinator's atomic between-window stop mechanism."""
import datetime,hashlib,json,os,socket,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;old=ws/'parent4-operational-sat-20261019';new=ws/'product-classical-nine-operational-20261019'
assert socket.gethostname()=='LHC-104-070' and not (r/'REQUEST.json').exists()
assert (new/'prepare.exit').read_text().strip()=='0' and (new/'control.exit').read_text().strip()=='0'
acc=json.loads((new/'ACCEPTANCE.json').read_text());assert acc['failure_gate_pass'] and acc['cost_gate_pass']
assert json.loads((new/'CONTROL.json').read_text())['status']=='CONTROL_ROWS_EQUAL_QUALIFIED_PREFIX'
assert not (old/'search.exit').exists() and not list((old/'passes').glob('pass-*.json'))
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
assert sha(new/'tool/target/release/value_prefilter')==acc['operational_binary_sha256']
assert all(sha(Path(p))==h for p,h in acc['runtime_artifacts'].items())
pids=[]
for lane in range(4):
    pid=int((old/f'worker{lane}.pid').read_text());assert Path(f'/proc/{pid}/cwd').resolve()==old
    assert Path(f'/proc/{pid}/exe').resolve()==old/'tool/target/release/value_prefilter'
    assert not '\nState:\tZ' in Path(f'/proc/{pid}/status').read_text();pids.append(pid)
candidate=ws/'product-pareto-20261019/candidate-parent4'
state={'hostname':socket.gethostname(),'candidate_head':subprocess.check_output(['git','-C',str(candidate),'rev-parse','HEAD'],text=True).strip(),'candidate_branch':subprocess.check_output(['git','-C',str(candidate),'branch','--show-current'],text=True).strip(),'candidate_status':subprocess.check_output(['git','-C',str(candidate),'status','--porcelain'],text=True),'worker_pids_verified':pids}
tmp=r/'stop-after-complete-window.txt'
with tmp.open('x') as f:f.write('0\n');f.flush();os.fsync(f.fileno())
assert not list((old/'passes').glob('pass-*.json'))
# Atomic hard-link publication refuses to overwrite any concurrently selected pass.
os.link(tmp,old/'stop-after-nonce.txt')
receipt={'status':'CLEAN_BETWEEN_WINDOW_STOP_REQUESTED','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reason':'Superseded by the genuinely lower-Toffoli frozen classical9 circuit after all source/gate/runtime/cost/prefix checks pass',
 'new_acceptance_sha256':sha(new/'ACCEPTANCE.json'),'new_control_sha256':sha(new/'CONTROL.json'),'old_source_and_runtime_unchanged':True,'old_logs_preserved':True,'no_process_kill_or_source_edit':True,'verified_state':state,
 'remaining':'Wait for old search.exit and terminal summary. If any pass appears, preserve/resolve it before launching the replacement.'}
(r/'REQUEST.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
