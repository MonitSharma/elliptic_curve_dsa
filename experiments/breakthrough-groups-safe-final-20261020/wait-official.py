import json,subprocess,time,urllib.request
from pathlib import Path
r=Path(__file__).resolve().parent;start=time.time();last=None
try:
 while not(r/'submission-response.json').exists() or not(r/'upload.exit').exists():assert time.time()-start<2400;time.sleep(3)
 assert(r/'upload.exit').read_text().strip()=='0';sid=json.loads((r/'submission-response.json').read_text())['submission']['id']
 while True:
  with urllib.request.urlopen('https://api.ecdsa.fail/api/submissions/'+sid,timeout=60) as response:data=json.load(response)
  s=data['submission'];state=(s['status'],s.get('officialMetrics'),s.get('submissionCommitSha'));(r/'submission-status.json').write_text(json.dumps(data,indent=2)+'\n')
  if state!=last:print(json.dumps({'id':sid,'status':s['status'],'officialMetrics':s.get('officialMetrics'),'officialScore':s.get('officialScore'),'rejectionReason':s.get('rejectionReason')}),flush=True);last=state
  if s.get('officialMetrics') and(s['status']=='accepted' or s['status']=='rejected' and s.get('rejectionReason')=='score did not improve current best'):subprocess.run(['python3',str(r/'verify-official-source.py')],cwd=r,check=True);break
  if s['status'] in ['failed','rejected','cancelled']:raise RuntimeError('Official verification failed; preserve result, never blindly resubmit')
  assert time.time()-start<2400;time.sleep(30)
 (r/'official-check.exit').write_text('0\n')
except Exception:
 (r/'official-check.exit').write_text('1\n');raise
