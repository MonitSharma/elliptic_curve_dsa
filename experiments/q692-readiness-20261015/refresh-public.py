"""Read-only public refresh; save only into this experiment's own directory."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,importlib.util,json,sys,urllib.request
root=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('leaderboard',root/'scripts/analyze-leaderboard.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
dest=Path(__file__).resolve().parent/'public-refresh';dest.mkdir(exist_ok=True)
raw={}
for name,url in [('benchmark',module.API),('submissions',module.API+'/submissions')]:
 with urllib.request.urlopen(url,timeout=60) as response:raw[name]=response.read()
 (dest/(name+'.json')).write_bytes(raw[name])
summary=module.analyze(json.loads(raw['submissions'])['submissions'],json.loads(raw['benchmark'])['benchmark'])
summary['raw_sha256']={k:hashlib.sha256(v).hexdigest()for k,v in raw.items()}
summary['benchmark']=json.loads(raw['benchmark'])['benchmark']
(dest/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:summary[k]for k in ['analyzed_at','record_count','eligible_count','leaders','targets']},indent=2))
