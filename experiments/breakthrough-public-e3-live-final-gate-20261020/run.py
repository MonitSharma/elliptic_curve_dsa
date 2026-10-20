import subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent
try:
 start=time.time();source=ws/'breakthrough-public-e3-live-finished-20261020';dev=ws/'breakthrough-public-e3-live-development-20261020'
 while not(source/'run.exit').exists()or not(dev/'DEVELOPMENT-CONTROLLER.exit').exists():assert time.time()-start<7200;time.sleep(2)
 assert(source/'run.exit').read_text().strip()=='0'and(dev/'DEVELOPMENT-CONTROLLER.exit').read_text().strip()=='0';subprocess.run(['python3',str(r/'declare.py')],cwd=r,check=True);subprocess.run(['python3',str(r/'census.py')],cwd=r,check=True);(r/'controller.exit').write_text('0\n')
except Exception:
 (r/'controller.exit').write_text('1\n');raise
