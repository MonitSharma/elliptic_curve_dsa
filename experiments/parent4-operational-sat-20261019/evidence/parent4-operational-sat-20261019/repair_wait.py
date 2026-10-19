import json,os,signal,time
from pathlib import Path
r=Path(__file__).resolve().parent
actual=r.parent/'product-parent-sat-20261019/parent4-filter/filter.exit'
assert actual.read_text().strip()=='0'
pid=int((r/'prepare.pid').read_text())
assert Path(f'/proc/{pid}/cwd').resolve()==r
cmd=Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0')
assert cmd[:2]==[b'bash',b'run-prepare.sh'] and os.getpgid(pid)==pid
assert not (r/'tool').exists()
record={'reason':'Completed validation EXIT trap used its output working directory; dependent v1 waited for a different path.',
    'genuine_filter_exit_path':str(actual),'genuine_filter_exit':0,'stopped_waiting_pid':pid,
    'old_preparation_had_not_built_a_tool':True,'exit_marker_manually_created':False}
(r/'PREPARE-V1-PATH-ERROR.json').write_text(json.dumps(record,indent=2)+'\n')
os.killpg(pid,signal.SIGTERM)
for _ in range(50):
    if (r/'prepare.exit').exists():break
    time.sleep(.1)
assert (r/'prepare.exit').exists(),'Original shell did not write its genuine terminal exit'
record['genuine_original_launcher_exit']=(r/'prepare.exit').read_text().strip()
(r/'PREPARE-V1-PATH-ERROR.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record),flush=True)
