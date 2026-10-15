from pathlib import Path
import json,subprocess
root=Path(__file__).resolve().parent
assert not (root/'launch.pid').exists(),'never restart an existing proof trial'
check=json.loads(subprocess.check_output(['python3','/home/hclau/ecdsa_research/server-preflight.py']))
assert check['hostname']=='LHC-104-070' and check['memory']['MemAvailable_bytes']>=124*1024**3
(root/'launch-preflight.json').write_text(json.dumps(check,indent=2)+'\n')
with (root/'launch.log').open('w') as out:
    job=subprocess.Popen(['nohup','bash',str(root/'run.sh')],cwd=root,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
(root/'launch.pid').write_text(str(job.pid)+'\n');print(job.pid)
