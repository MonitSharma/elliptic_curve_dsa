import json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent
assert not (r/'build.pid').exists() and not (r/'watch.pid').exists()
assert json.loads((r.parent/'classical9-final-v2-20261019/READY.json').read_text())['status']=='COPIED_BOUND_AUDITOR_AND_ALL_NATIVE_RUNTIME_GATE_PATHS_PASS'
pid=int((r.parent/'classical9-final-v2-20261019/watch.pid').read_text());assert Path('/proc',str(pid),'cwd').resolve()==r.parent/'classical9-final-v2-20261019'
with (r/'build-nohup.log').open('xb') as f:p=subprocess.Popen(['nohup','bash','run-build.sh'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'build.pid').write_text(str(p.pid)+'\n')
print(json.dumps({'build_pid':p.pid,'new_source_nonces_allowed':False,'next':'Launch the idle waiter only after BUILD_PREPARED exists.'}))
