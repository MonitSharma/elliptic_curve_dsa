from pathlib import Path
import subprocess
r=Path(__file__).resolve().parent
assert not (r/'launch.pid').exists()
with (r/'launch.log').open('w') as out:
    p=subprocess.Popen(['nohup','bash',str(r/'run.sh')],cwd=r,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
(r/'launch.pid').write_text(str(p.pid)+'\n');print(p.pid)
