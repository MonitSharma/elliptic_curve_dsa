"""Stop only the recorded stale-path waiting manager, after v2 is live."""
import json,os,signal,time
from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'parent4-final-sat-20261019';s=r.parent/'parent4-operational-sat-20261019'
assert not (s/'search.exit').exists(),'inspect terminal search before replacing managers'
new_pid=int((r/'watch.pid').read_text());old_pid=int((old/'watch.pid').read_text())
assert old_pid==610395 and old_pid!=new_pid
assert Path(f'/proc/{new_pid}/cwd').resolve()==r
assert Path(f'/proc/{old_pid}/cwd').resolve()==old
assert Path(f'/proc/{new_pid}/cmdline').read_bytes().split(b'\0')[:2]==[b'python3',b'watch.py']
assert Path(f'/proc/{old_pid}/cmdline').read_bytes().split(b'\0')[:2]==[b'python3',b'watch.py']
assert not (old/'WATCH_RESULT.json').exists()
os.kill(old_pid,signal.SIGTERM)
for _ in range(50):
    p=Path(f'/proc/{old_pid}/stat')
    if not p.exists() or p.read_text().split()[2]=='Z':break
    time.sleep(.1)
else:raise RuntimeError('old waiting manager has not terminated; do not kill unrelated jobs')
result={'status':'STALE_PATH_WAITING_MANAGER_REPLACED','old_pid':old_pid,'new_pid':new_pid,
        'old_source_and_pid_records_preserved':True,'search_and_frozen_source_unchanged':True,
        'reason':'finalize.py referenced the old product67 qualification directory rather than the frozen parent4 gate/archive',
        'correct_path_control':json.loads((r/'PATH-CONTROL.json').read_text())}
(r/'SWITCH.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='correct_path_control'}))
