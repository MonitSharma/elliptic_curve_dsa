"""Read current public leaders without overwriting another chat's shared figures."""
from pathlib import Path
import datetime,hashlib,json,sys,urllib.request
dest=Path(sys.argv[1]);assert dest.suffix=='.json'
url='https://api.ecdsa.fail/api/benchmarks/1ffb695a-309b-46b6-a728-2f97d8c7be74/submissions'
with urllib.request.urlopen(url,timeout=45) as response:raw=response.read()
records=json.loads(raw)['submissions'];valid=[]
for record in records:
    metric=record.get('officialMetrics') or {};q=metric.get('qubits');t=metric.get('toffoli')
    status=record.get('status')=='accepted' or record.get('status')=='rejected' and record.get('rejectionReason')=='score did not improve current best'
    if status and type(q) is int and type(t) is int and min(q,t)>0 and record.get('officialScore')==q*t:valid.append(record)
assert valid
leaders={name:min(valid,key=key) for name,key in [('qubits',lambda r:r['officialMetrics']['qubits']),('toffoli',lambda r:r['officialMetrics']['toffoli']),('product',lambda r:r['officialScore'])]}
result={'checked_Singapore':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'public_source':url,'response_sha256':hashlib.sha256(raw).hexdigest(),'records':len(records),'eligible':len(valid),'leaders':{name:{k:r.get(k) for k in ['id','status','officialMetrics','officialScore','submissionCommitSha','solverUsername','rejectionReason']} for name,r in leaders.items()},'pending_753721_submission':next(({k:r.get(k) for k in ['id','status','officialMetrics','officialScore']} for r in records if r['id']=='03be8e19-ab3b-45c7-9c62-9d78970c4d95'),None),'shared_docs_or_figures_changed':False}
dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
