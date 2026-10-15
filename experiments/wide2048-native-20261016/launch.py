from pathlib import Path
import hashlib,json,subprocess
root=Path(__file__).resolve().parent
assert not (root/'launch.pid').exists(),'never restart an existing qualification'
check=json.loads(subprocess.check_output(['python3','/home/hclau/ecdsa_research/server-preflight.py']))
assert check['hostname']=='LHC-104-070' and check['memory']['MemAvailable_bytes']>=100*1024**3
(root/'launch-preflight.json').write_text(json.dumps(check,indent=2)+'\n')
reference=root/'reference753721.ops.bin'
assert hashlib.sha256(reference.read_bytes()).hexdigest()=='1d8c05eeee7b43dd694506b5efe963c771461b7e690bc62f409947b2306b7d77'
with (root/'launch.log').open('w') as out:
 job=subprocess.Popen(['nohup','bash',str(root/'run.sh')],cwd=root,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
(root/'launch.pid').write_text(str(job.pid)+'\n');print(job.pid)
