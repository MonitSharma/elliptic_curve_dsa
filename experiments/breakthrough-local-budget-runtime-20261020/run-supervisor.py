import subprocess
from pathlib import Path
r=Path(__file__).resolve().parent
raise SystemExit(subprocess.call(['bash',str(r/'run.sh')],cwd=r))
