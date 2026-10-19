import json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent
assert (r/'run.exit').read_text().strip()=='0'
assert not (r/'profile.pid').exists()
with (r/'profile-nohup.log').open('wb') as f:
    p=subprocess.Popen(['nohup','bash','run-profile.sh'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'profile.pid').write_text(str(p.pid)+'\n')
print(json.dumps({'pid':p.pid,'directory':str(r),'job':'instrument-exact-peak-coverage'}))
