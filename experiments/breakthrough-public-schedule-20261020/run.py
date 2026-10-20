import subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'observer'
for args,log,cwd in[(['python3','prepare.py'],'prepare.log',r),(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','build_circuit'],'build.log',t),(['python3','sweep.py'],'sweep.log',r)]:
 with(r/log).open('xb')as out:p=subprocess.Popen(args,cwd=cwd,stdout=out,stderr=subprocess.STDOUT);rc=p.wait()
 if rc:break
(r/'run.exit').write_text(str(rc)+'\n');raise SystemExit(rc)
