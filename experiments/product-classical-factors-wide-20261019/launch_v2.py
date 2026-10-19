import json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent
assert (r/'run.exit').read_text().strip()=='101' and not (r/'run-v2.pid').exists()
assert 'error[E0753]' in (r/'tests.log').read_text()
with (r/'nohup-v2.log').open('xb') as f:
    p=subprocess.Popen(['nohup','bash','run-v2.sh'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'run-v2.pid').write_text(str(p.pid)+'\n');print(json.dumps({'pid':p.pid,'job':'source-only512-bit-factor-screen-after-doc-comment-compile-fix'}))
