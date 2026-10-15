"""Copy bounded evidence; keep failed and unscored experiments explicit."""
from pathlib import Path
import hashlib,json,re,shutil
from datetime import datetime,timezone
root=Path(__file__).resolve().parent
out=root/'collected';out.mkdir(exist_ok=True)
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        while b:=f.read(8*1024*1024):h.update(b)
    return h.hexdigest()
paths={}
for folder in ['evidence','wide-evidence','replay','wide-replay']:
    for p in (root/folder).rglob('*'):
        if not p.is_file() or 'target' in p.relative_to(root).parts:continue
        if p.suffix in ['.log','.json','.patch','.sha256','.exit','.rs','.toml'] or p.name in ['Cargo.lock','rust-toolchain']:
            paths[str(p.relative_to(root))]=p
for p in root.iterdir():
    if p.is_file() and p.suffix in ['.pid','.exit','.log','.sh','.py','.rs']:
        paths[str(p.relative_to(root))]=p
for name,p in paths.items():
    target=out/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
summaries={}
for folder,output in [('replay','paired-summary.json'),('wide-replay','wide-paired-summary.json')]:
    records={}
    for mode in ['independent','structured','candidate']:
        p=root/folder/(mode+'.log')
        if not p.exists():continue
        lines=re.findall(r'DIAGNOSTIC_ONLY .*',p.read_text())
        if not lines:continue
        row={}
        for key,value in re.findall(r'(\w+)=([\w.\-]+)',lines[-1]):
            row[key]=float(value) if '.' in value else int(value) if value.lstrip('-').isdigit() else value
        records[mode]=row
    (out/output).write_text(json.dumps(records,indent=2)+'\n')
    summaries[folder]=records
raw={}
for p in [root/'candidate-b3-cache-v1/ops.bin',root/'candidate-wide-v1/ops.bin',*list((root/'replay').glob('*.tsv')),*list((root/'wide-replay').glob('*.tsv'))]:
    if p.exists():raw[str(p)]={'sha256':digest(p),'bytes':p.stat().st_size}
manifest={'created_at_utc':datetime.now(timezone.utc).isoformat(),
    'qualified_score':None,'status':'NO_QUALIFIED_RECORD','replays':summaries,
    'server_artifacts':raw,'files':{name:digest(out/name) for name in paths}}
(out/'evidence-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'replays':summaries,'file_count':len(paths)},indent=2))
