import json,subprocess,sys
from pathlib import Path
r=Path(__file__).resolve().parent
name=sys.argv[1];script=r/('run-'+name+'.sh')
assert name.isalpha() and script.is_file()
assert not (r/(name+'.pid')).exists()
with (r/(name+'.nohup.log')).open('wb') as f:
    p=subprocess.Popen(['nohup','bash',str(script)],cwd=r,stdin=subprocess.DEVNULL,
        stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/(name+'.pid')).write_text(str(p.pid)+'\n')
print(json.dumps({'pid':p.pid,'job':name,'directory':str(r)}))
