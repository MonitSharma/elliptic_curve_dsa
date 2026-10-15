"""Collect bounded research artifacts, retaining failures and unscored labels."""
import hashlib
import json
from pathlib import Path
import re
import shutil
from datetime import datetime,timezone

root=Path(__file__).resolve().parent
out=root/'collected';out.mkdir(exist_ok=True)
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        while b:=f.read(8*1024*1024):h.update(b)
    return h.hexdigest()
paths={}
for folder in ['erase-audit','pebble-audit','pebble-audit-v2','cache-audit','cache-audit-v2','cache-audit-v3','lazy-cache-audit','lazy-cache-native-v2','lazy-cache-native-v3','lazy-cache-native-v4','cache-replay','cache-replay-v2']:
    for name in ['analysis.log','tests.log','build.log','source.sha256','preflight.json','run.exit','bindings.sha256','independent.log','structured.log','candidate.log']:
        p=root/folder/name
        if p.exists():paths[f'{folder}/{name}']=p
for name in ['benchmark.log','native.log','binaries.sha256','preflight.json','benchmark.exit','run.exit','terminal/receipt.json','terminal/candidate.patch']:
    p=root/'candidate-lazy-v1-evidence'/name
    if p.exists():paths[f'candidate/{name}']=p
for p in root.glob('*launch.log'):paths[f'launches/{p.name}']=p
for p in root.glob('*.pid'):paths[f'pids/{p.name}']=p
for p in root.glob('*.sh'):paths[f'launchers/{p.name}']=p
for key,p in paths.items():
    target=out/key;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
replays={}
for family in ['independent','structured','candidate']:
    p=root/'cache-replay-v2'/f'{family}.log'
    if p.exists():
        text=p.read_text();matches=re.findall(r'DIAGNOSTIC_ONLY .*',text)
        replays[family]={'terminal':bool(matches),'summary':matches[-1] if matches else None,'sha256':digest(p)}
raw={}
for p in [root/'peak-classes.json',root/'candidate-lazy-v1/ops.bin',*[root/'cache-replay-v2'/f'{k}.tsv' for k in replays]]:
    if p.exists():raw[str(p)]={'bytes':p.stat().st_size,'sha256':digest(p)}
for p in (root/'cache-replay-v2/crate/src').glob('*.rs'):
    target=out/'replay-source'/p.name;target.parent.mkdir(exist_ok=True);shutil.copyfile(p,target)
manifest={'collected_at_utc':datetime.now(timezone.utc).isoformat(),'status':'FAILED_OFFICIAL_BENCHMARK_REPLAY_DIAGNOSTIC','qualified_score':None,'replays':replays,'server_raw_artifacts':raw,'files':{k:digest(out/k) for k in paths}}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'replays':replays,'files':len(paths)},indent=2))
