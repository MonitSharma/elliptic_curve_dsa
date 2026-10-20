import subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent
try:
 subprocess.run(['python3',str(r/'finalize.py')],cwd=r,check=True)
 subprocess.run(['python3',str(r/'seal.py')],cwd=r,check=True)
 (r/'review.exit').write_text('0\n')
except BaseException:
 (r/'review.exit').write_text('1\n');raise
