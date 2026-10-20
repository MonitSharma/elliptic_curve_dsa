from pathlib import Path
import subprocess
r=Path(__file__).resolve().parent
with(r/'search.log').open('xb')as log:
 p=subprocess.Popen(['python3',str(r/'search.py')],cwd=r,stdout=log,stderr=subprocess.STDOUT);(r/'search.pid').write_text(str(p.pid)+'\n');rc=p.wait()
(r/'run.exit').write_text(str(rc)+'\n');assert rc==0
