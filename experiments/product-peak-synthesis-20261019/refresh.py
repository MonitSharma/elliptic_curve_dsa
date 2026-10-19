import importlib.util,json,urllib.request,hashlib
from pathlib import Path
p=Path('experiments/product-peak-synthesis-20261019')
spec=importlib.util.spec_from_file_location('board','scripts/analyze-leaderboard.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
raw={}
for name,url in [('submissions',m.API+'/submissions'),('benchmark',m.API)]:
    data=urllib.request.urlopen(url,timeout=45).read(); (p/(name+'.json')).write_bytes(data); raw[name]=json.loads(data)
s=m.analyze(raw['submissions']['submissions'],raw['benchmark']['benchmark'])
s['input_sha256']={name:hashlib.sha256((p/(name+'.json')).read_bytes()).hexdigest() for name in raw}
(p/'leaderboard.json').write_text(json.dumps(s,indent=2))
for name,lead in s['leaders'].items():
    full=next(x for x in raw['submissions']['submissions'] if x['id']==lead['id']); (p/('leader-'+name+'.json')).write_text(json.dumps(full,indent=2))
print(json.dumps({k:s[k] for k in ['analyzed_at','record_count','leaders','targets']},indent=2))


