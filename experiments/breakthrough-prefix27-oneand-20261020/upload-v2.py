"""Supply model inputs locally; v1 failed before any search on missing server model."""
import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'breakthrough-prefix-dag-20261020';fun=r.parent/'breakthrough-live-core-rank-20261020'
s=(r/'search.py').read_text();a="for name in ['PREFIX-DAG.json','PROTECTED-v3-c1+c2+c3+c4+tt.json','generate-native-schedule.py']:\n shutil.copyfile(old/name,r/name)\nsource=(old/'generate-native-cleanup.py').read_text();";assert a in s;s=s.replace(a,"source=(r/'original-generate-native-cleanup.py').read_text().replace(\"r.parent/'breakthrough-live-core-rank-20261020'\",'r');")
s=s.replace("(old/'generate-native-cleanup.py').read_bytes()","(r/'original-generate-native-cleanup.py').read_bytes()")
(r/'search-v2.py').write_bytes(s.encode());dest='smu_server:/home/hclau/ecdsa_research/breakthrough-prefix27-oneand-20261020/'
files=[old/'PREFIX-DAG.json',old/'PROTECTED-v3-c1+c2+c3+c4+tt.json',old/'generate-native-schedule.py',fun/'FUNCTIONS.json',fun/'QUADRATIC-LOAN-REVERSE-MODEL.json',r/'search-v2.py']
subprocess.run(['scp',*[str(p)for p in files],dest],check=True);subprocess.run(['scp',str(old/'generate-native-cleanup.py'),dest+'original-generate-native-cleanup.py'],check=True)
(r/'SEARCH-INPUTS.json').write_text(json.dumps({'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in files},'original-generate-native-cleanup.py':hashlib.sha256((old/'generate-native-cleanup.py').read_bytes()).hexdigest(),'v1_failure':'Missing model file on server; no search ran. V2 supplies immutable model inputs and adjusts only paths.'},indent=2)+'\n');subprocess.run(['scp',str(r/'SEARCH-INPUTS.json'),dest],check=True)
subprocess.run(['ssh','smu_server','python3 /home/hclau/ecdsa_research/breakthrough-sparse-polynomial-20261020/launch-job.py breakthrough-prefix27-oneand-20261020 search-v2.py supervisor-v2'],check=True)
