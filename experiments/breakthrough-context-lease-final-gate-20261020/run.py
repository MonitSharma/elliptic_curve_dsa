import subprocess
from pathlib import Path
r=Path(__file__).resolve().parent
try:
 subprocess.run(['python3',str(r/'declare.py')],check=True,cwd=r)
 subprocess.run(['python3',str(r/'census.py')],check=True,cwd=r)
 (r/'controller.exit').write_text('0\n')
except BaseException:
 (r/'controller.exit').write_text('1\n');raise
