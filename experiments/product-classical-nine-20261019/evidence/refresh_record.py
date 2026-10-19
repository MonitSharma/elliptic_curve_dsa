import urllib.request,json,hashlib,time
from pathlib import Path
from datetime import datetime,timezone
r=Path(__file__).resolve().parent
api='https://api.ecdsa.fail/api/benchmarks/1ffb695a-309b-46b6-a728-2f97d8c7be74'
for name,url in [('submissions',api+'/submissions'),('benchmark',api)]:
    for attempt in range(3):
        try:
            data=urllib.request.urlopen(url,timeout=45).read();break
        except Exception:
            if attempt==2:raise
            time.sleep(3)
    (r/(name+'.json')).write_bytes(data)
rows=json.loads((r/'submissions.json').read_text())['submissions']
eligible=[x for x in rows if (x.get('status')=='accepted' or (x.get('status')=='rejected' and x.get('rejectionReason')=='score did not improve current best')) and isinstance(x.get('officialScore'),int) and x['officialScore']>0 and x['officialScore']==(x.get('officialMetrics') or {}).get('qubits',0)*(x.get('officialMetrics') or {}).get('toffoli',0)]
leader=min(eligible,key=lambda x:x['officialScore'])
out={'at_utc':datetime.now(timezone.utc).isoformat(),'leader':leader,
     'sha256':{name:hashlib.sha256((r/(name+'.json')).read_bytes()).hexdigest() for name in ('submissions','benchmark')}}
(r/'PUBLIC-RECORD.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:leader[k] for k in ('id','officialScore','officialMetrics','submissionCommitSha')}))
