import json,shutil,urllib.request
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent;sid=json.loads((r/'submission-response.json').read_text())['submission']['id']
if(r/'submission-status.json').exists()and not(r/'status-initial.json').exists():shutil.copyfile(r/'submission-status.json',r/'status-initial.json')
with urllib.request.urlopen('https://api.ecdsa.fail/api/submissions/'+sid,timeout=60)as response:data=json.load(response)
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');payload=json.dumps(data,indent=2)+'\n';(r/('status-'+stamp+'.json')).write_text(payload);(r/'submission-status.json').write_text(payload);s=data['submission'];print(json.dumps({k:s.get(k)for k in['id','status','officialMetrics','officialScore','rejectionReason','submissionCommitSha','promotionStatus']},indent=2));print('top_keys',list(data))
for key in['job','validationJob','validation']:
 if key in data:print(key,json.dumps(data[key],indent=2)[:6000])
