import hashlib,json,os,shutil,socket,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;old=ws/'parent4-operational-sat-20261019'
assert socket.gethostname()=='LHC-104-070'
assert (old/'search.exit').read_text().strip()=='0'
terminal=json.loads((old/'RESULT.json').read_text());assert terminal['best_full_protected_pass'] is None and terminal['worker_exit_codes']==[0]*4
assert not list((old/'passes').glob('pass-*.json')),'Preserve and resolve any old pass before launching'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
acc=json.loads((r/'ACCEPTANCE.json').read_text());assert acc['failure_gate_pass'] and acc['cost_gate_pass']
assert (r/'control.exit').read_text().strip()=='0' and json.loads((r/'CONTROL.json').read_text())['status']=='CONTROL_ROWS_EQUAL_QUALIFIED_PREFIX'
assert sha(r/'tool/target/release/value_prefilter')==acc['operational_binary_sha256']
assert all(sha(Path(p))==h for p,h in acc['runtime_artifacts'].items())
assert json.loads((ws/'classical9-final-20261019/PATH-CONTROL.json').read_text())['status']=='CLASSICAL9_FINALIZER_ALL_INPUT_PATHS_AND_HASHES_PASS'
watch=int((ws/'classical9-final-20261019/watch.pid').read_text());assert Path(f'/proc/{watch}/cwd').resolve()==ws/'classical9-final-20261019'
env=dict(os.environ,RESEARCH_SLOTS='60')
profile=json.loads(subprocess.check_output(['python3',str(ws/'autonomous-20261019/preflight_v13.py')],env=env,text=True))
assert not profile['active_search_workers'] and profile['total_reserved_research_slots']<=64
public=json.loads((r/'PUBLIC-RECORD.json').read_text())['leader'];gate=acc['failure_gate']
assert public['officialScore']>0 and public['officialScore']==public['officialMetrics']['qubits']*public['officialMetrics']['toffoli']
assert 1234*gate['mean_toffoli']['candidate']<public['officialScore'],'Diagnostic mean no longer targets the current product; do not start automatically'
assert shutil.disk_usage(r).free>200*1024**3
record={**profile,'hostname':socket.gethostname(),'threads_each':14,'workers':4,'submission_mode':'queue','source_frozen':True,
 'public_product_parent':public['id'],'public_record_sha256':sha(r/'PUBLIC-RECORD.json'),'source_gate_is_final':True,'old_search_terminal_preserved':True,'scheduler_available':shutil.which('squeue') is not None,
 'old_search_retirement_sha256':sha(ws/'parent4-retirement-20261019/TERMINAL.json')}
print(json.dumps(record,indent=2))
