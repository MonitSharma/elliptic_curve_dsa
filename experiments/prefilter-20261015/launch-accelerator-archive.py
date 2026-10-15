from pathlib import Path
import subprocess,os
r=Path(__file__).parent
log=(r/'evidence/archive-accelerator-supplement.log').open('w')
p=subprocess.Popen(['nohup','python3',str(r/'archive-evidence.py'),'--terminal-only','--accelerator-supplement'],cwd=r,stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True)
(r/'evidence/archive-accelerator-supplement.pid').write_text(str(p.pid)+'\n')
print(p.pid)
