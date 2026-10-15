"""Archive completed external cache experiments without copying large streams."""
from pathlib import Path
from datetime import datetime,timezone
import subprocess,hashlib,json,gzip,tarfile
root=Path(__file__).resolve().parent;out=root/'collected';assert not out.exists();out.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest()
files={}
def save(p,rel):
    b=p.read_bytes();q=out/rel;q.parent.mkdir(parents=True,exist_ok=True)
    if len(b)>262144:q=q.with_suffix(q.suffix+'.gz');q.write_bytes(gzip.compress(b,mtime=0))
    else:q.write_bytes(b)
    files[rel]={'source_sha256':sha(b),'archive_sha256':sha(q.read_bytes()),'bytes':len(b),'path':str(q.relative_to(out))}
for p in sorted(root.iterdir()):
    if p.is_file() and p.suffix in ['.log','.json','.sha256','.pid','.exit','.py','.sh','.rs','.tsv']:save(p,p.name)
for d in ['analyzer','replay']:
    if (root/d).exists():
        for p in (root/d).rglob('*'):
            if p.is_file() and 'target' not in p.parts:save(p,str(p.relative_to(root)))
repo=root.parent/'overnight-20261014/product-b3-baseline'
call=lambda *a:subprocess.check_output(['git','-C',str(repo),*a])
rev=call('rev-parse','HEAD').decode().strip();protected={}
for rel in call('ls-files').decode().splitlines():
    if not rel.startswith('src/point_add/'):
        b=(repo/rel).read_bytes();assert b==call('show',rev+':'+rel);protected[rel]=sha(b)
streams={p.name:sha(p.read_bytes()) for p in root.glob('*.bin')}
diagnostics={p.name:[s for s in p.read_text().splitlines() if s.startswith(('DIAGNOSTIC_ONLY','RECONSTRUCTION_OK','LAZY_SUMMARY','test result:'))] for p in root.glob('*.log')}
diagnostics={k:v for k,v in diagnostics.items() if v}
receipt={'collected_at':datetime.now(timezone.utc).isoformat(),'status':'terminal component experiment; no qualified score','score':None,'official_benchmark_run':False,'submission_made':False,'baseline_revision':rev,'baseline_status':call('status','--porcelain').decode(),'protected_unchanged':True,'protected_sha256':protected,'stream_sha256':streams,'exit_codes':{p.name:int(p.read_text()) for p in root.glob('*.exit')},'diagnostics':diagnostics,'archives':files}
# Retention used the previously frozen independent reconstructor.
if not (root/'replay').exists():
    old=root.parent/'toffoli-readiness-20261015/wide-replay'
    save(old/'crate/src/main.rs','external-replay/main.rs');save(old/'crate/Cargo.toml','external-replay/Cargo.toml')
    receipt['replay_binary_sha256']=sha((old/'paired_diagnostic').read_bytes())
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
with tarfile.open(root/'evidence.tar.gz','w:gz') as tar:tar.add(out,arcname='evidence')
print(json.dumps({'streams':streams,'diagnostics':diagnostics,'exit_codes':receipt['exit_codes'],'artifacts':len(files)},indent=2))
