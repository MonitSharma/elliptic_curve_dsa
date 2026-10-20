from pathlib import Path
import shutil,ast
root=Path(__file__).resolve().parents[2];old=root/'experiments/breakthrough-native-both-final-20261020';r=root/'experiments/breakthrough-native-context-final-20261020';shutil.copyfile(old/'check-status.py',r/'check-status.py')
s=(old/'verify-official-source.py').read_text();changes={'d182a53e-be3d-4119-8298-303a9a9de07a':'38a686dd-a2b1-4bdc-899e-81a389d36fd5',"{'qubits':1464,'toffoli':748691}":"{'qubits':1480,'toffoli':748184}",'1096083624':'1107312320','len(paths)==200':'len(paths)==201','cec71544f16da5598921a8a04e3b1416bda6f28d01878b1101ac724157a6f536':'0e4fcfab22855197075ce69bb8e2b067f7fbf22d4412390707df3944831f0689',"'Q':1464,'T':748691":"'Q':1480,'T':748184","'improvement_in_T':2014":"'improvement_in_T':507"}
for x,y in changes.items():assert x in s,x;s=s.replace(x,y)
ast.parse(s);(r/'verify-official-source.py').write_text(s)
(r/'wait-official.py').write_text('''import json,subprocess,time,urllib.request
from pathlib import Path
r=Path(__file__).resolve().parent;start=time.time();last=None
try:
 sid=json.loads((r/'submission-response.json').read_text())['submission']['id'];assert sid=='38a686dd-a2b1-4bdc-899e-81a389d36fd5'
 while True:
  with urllib.request.urlopen('https://api.ecdsa.fail/api/submissions/'+sid,timeout=60)as response:data=json.load(response)
  s=data['submission'];state=(s['status'],s.get('officialMetrics'),s.get('submissionCommitSha'));(r/'submission-status.json').write_text(json.dumps(data,indent=2)+'\\n')
  if state!=last:print(json.dumps({'id':sid,'status':s['status'],'officialMetrics':s.get('officialMetrics'),'officialScore':s.get('officialScore'),'rejectionReason':s.get('rejectionReason')}),flush=True);last=state
  if s.get('officialMetrics')and(s['status']=='accepted'or s['status']=='rejected'and s.get('rejectionReason')=='score did not improve current best'):subprocess.run(['python3',str(r/'verify-official-source.py')],cwd=r,check=True);break
  if s['status']in['failed','rejected','cancelled']:raise RuntimeError('Official verification failed; preserve result, never blindly resubmit')
  assert time.time()-start<2400;time.sleep(30)
 (r/'official-check.exit').write_text('0\\n')
except Exception:
 (r/'official-check.exit').write_text('1\\n');raise
''');print(r)
