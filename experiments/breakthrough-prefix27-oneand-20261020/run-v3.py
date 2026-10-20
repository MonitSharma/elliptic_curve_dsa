from pathlib import Path
import subprocess
r=Path(__file__).resolve().parent
with(r/'prepare-v3.log').open('xb')as log:rc=subprocess.run(['python3',str(r/'prepare-v3.py')],stdout=log,stderr=subprocess.STDOUT).returncode
assert rc==0
with(r/'search-v3.log').open('xb')as log:
 p=subprocess.Popen(['timeout','1800','python3',str(r/'search-v3.py')],stdout=log,stderr=subprocess.STDOUT);(r/'search-v3.pid').write_text(str(p.pid)+'\n');rc=p.wait()
(r/'search-v3.exit').write_text(str(rc)+'\n');assert rc==0
