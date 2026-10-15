from pathlib import Path
import subprocess,os
r=Path(__file__).parent
log=(r/'evidence/archive-mask-v3.log').open('w')
p=subprocess.Popen(['nohup','python3',str(r/'archive-evidence.py'),'--terminal-only'],cwd=r,stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True)
(r/'evidence/archive-mask-v3.pid').write_text(str(p.pid)+'\n')
print(p.pid)
