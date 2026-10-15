"""Preserve both terminal rail-margin variants and protected-source bindings."""
from pathlib import Path
from datetime import datetime,timezone
import subprocess,hashlib,json,gzip,tarfile
root=Path(__file__).resolve().parent;out=root/'collected';assert not out.exists();out.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest();archives={}
def save(p,rel):
    b=p.read_bytes();q=out/rel;q.parent.mkdir(parents=True,exist_ok=True)
    if len(b)>262144:q=q.with_suffix(q.suffix+'.gz');q.write_bytes(gzip.compress(b,mtime=0))
    else:q.write_bytes(b)
    archives[rel]={'source_sha256':sha(b),'archive_sha256':sha(q.read_bytes()),'bytes':len(b),'path':str(q.relative_to(out))}
for p in sorted(root.iterdir()):
    if p.is_file() and p.suffix in ['.log','.json','.sha256','.patch','.pid','.exit','.py','.sh']:save(p,p.name)
repos={}
for name in ['margin-one-b3','margin-room-b3']:
    repo=root/name;call=lambda *a:subprocess.check_output(['git','-C',str(repo),*a])
    rev=call('rev-parse','HEAD').decode().strip();changed=call('diff','--name-only').decode().splitlines();assert all(p.startswith('src/point_add/') for p in changed)
    assert not call('ls-files','--others','--exclude-standard').strip()
    protected={}
    for rel in call('ls-files').decode().splitlines():
        if not rel.startswith('src/point_add/'):
            b=(repo/rel).read_bytes();assert b==call('show',rev+':'+rel);protected[rel]=sha(b)
    patch=call('diff','--binary');q=out/name/'source.patch';q.parent.mkdir();q.write_bytes(patch)
    stream=repo/'ops.bin'
    repos[name]={'revision':rev,'patch_sha256':sha(patch),'changed':changed,'protected_unchanged':True,'protected_sha256':protected,'stream_sha256':sha(stream.read_bytes()) if stream.exists() else None,'score':None}
old=root.parent/'arithmetic-repair-20261015'
save(old/'fixed-replay/src/main.rs','fixed-replay/main.rs');save(old/'fixed-replay/Cargo.toml','fixed-replay/Cargo.toml');save(old/'fixed-replay/Cargo.lock','fixed-replay/Cargo.lock')
for p in (old/'packets').glob('*.tsv'):save(p,'packets/'+p.name)
save(root.parent/'rail-repair-20261015/known15.tsv','packets/known15.tsv')
exits={p.name:int(p.read_text()) for p in root.glob('*.exit')};assert exits=={'run.exit':101,'room.exit':0}
fixed={p.name:[l for l in p.read_text().splitlines() if l.startswith('FIXED_DIAGNOSTIC')] for p in root.glob('room-*.log')};fixed={k:v for k,v in fixed.items() if v}
receipt={'collected_at':datetime.now(timezone.utc).isoformat(),'status':'terminal partial arithmetic repair; incorrect full circuit','score':None,'official_benchmark_run':False,'submission_made':False,'exit_codes':exits,'repos':repos,'fixed':fixed,'replay_binary_sha256':sha((old/'fixed-target/release/product_paired_diagnostic').read_bytes()),'binary_sha256':{name:sha((root/name/'release/build_circuit').read_bytes()) for name in ['target','room-target']},'limitations':['Same fixed input files, but unaligned measurement events across arithmetic rewrites.','Fifteen-shot replay has inactive lanes; its raw gate total is not a per-shot mean.','Headroom and planner allowance both change; causality requires a matched scratch-only control.','Structured and ten old-packet value failures remain.'],'archives':archives}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
with tarfile.open(root/'evidence.tar.gz','w:gz') as tar:tar.add(out,arcname='evidence')
print(json.dumps({'exit_codes':exits,'fixed':fixed,'artifacts':len(archives),'streams':{n:r['stream_sha256'] for n,r in repos.items()}},indent=2))
