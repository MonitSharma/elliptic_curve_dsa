import datetime,hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent
assert (r/'run.exit').read_text().strip()=='0'
assert not (r/'gate-v2.pid').exists() and not (r/'qualification').exists()
oldpid=int((r/'gate.pid').read_text());assert not Path(f'/proc/{oldpid}').exists()
assert b'pipefail\r: invalid option name' in (r/'gate-nohup.log').read_bytes()
assert b'\r' in (r/'run-gate.sh').read_bytes()
assert b'\r' not in (r/'run-gate-v2.sh').read_bytes()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(r/'GATE-ADMISSION-FAILURE.json').write_text(json.dumps({'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'SHELL_LINE_ENDING_ERROR_BEFORE_ANY_DECLARATION_OR_CENSUS','old_pid':oldpid,'old_script_sha256':sha(r/'run-gate.sh'),'old_log_sha256':sha(r/'gate-nohup.log'),'qualification_directory_absent_before_repair':True,'census_shots_executed':0,'frozen_candidate_unchanged':True,'gate_verdict_exists':False},indent=2)+'\n')
with (r/'gate-v2-nohup.log').open('xb') as f:
    p=subprocess.Popen(['nohup','bash','run-gate-v2.sh'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'gate-v2.pid').write_text(str(p.pid)+'\n')
print(json.dumps({'pid':p.pid,'job':'first-declared-final-classical9-gate-after-prelaunch-shell-repair'}))
