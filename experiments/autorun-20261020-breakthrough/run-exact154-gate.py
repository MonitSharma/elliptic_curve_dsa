import json,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;c=r.parent/'breakthrough-public140-exact154-20261020'
try:
 while not(c/'audit-v2.exit').exists():time.sleep(2)
 assert(c/'audit-v2.exit').read_text().strip()=='0'
 assert subprocess.call(['python3',str(r/'declare.py')],cwd=r)==0
 assert subprocess.call(['python3',str(r/'census.py')],cwd=r)==0
 (r/'controller.exit').write_text('0\n')
except BaseException:
 (r/'controller.exit').write_text('1\n');raise
