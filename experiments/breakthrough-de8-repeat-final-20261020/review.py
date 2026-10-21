import subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent
try:
 start=time.time()
 while not(r/'run.exit').exists():assert time.time()-start<21600;time.sleep(2)
 research=r.parent/'breakthrough-de8-repeat-finished-20261020'
 while not(research/'pipeline.exit').exists():assert time.time()-start<21600;time.sleep(2)
 assert(research/'pipeline.exit').read_text().strip()=='0'
 assert(r/'run.exit').read_text().strip()=='0';subprocess.run(['python3',str(r/'seal.py')],cwd=r,check=True);(r/'review.exit').write_text('0\n')
except Exception:
 (r/'review.exit').write_text('1\n');raise
