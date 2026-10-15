"""Preserve the terminal rail-repair checkpoint with source and protected-file bindings."""
from pathlib import Path
from datetime import datetime,timezone
import subprocess,hashlib,json,gzip,tarfile,os
root=Path(__file__).resolve().parent;out=root/'collected';assert not out.exists();out.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest()
def save(p,target):
    b=p.read_bytes();target.parent.mkdir(parents=True,exist_ok=True)
    if len(b)>262144:target=target.with_suffix(target.suffix+'.gz');target.write_bytes(gzip.compress(b,mtime=0))
    else:target.write_bytes(b)
    return {'source_sha256':sha(b),'bytes':len(b),'path':str(target.relative_to(out)),'archive_sha256':sha(target.read_bytes())}
archives={}
for p in sorted(root.iterdir()):
    if p.is_file() and p.suffix in ['.log','.json','.sha256','.patch','.pid','.exit','.rs','.py','.sh','.tsv']:
        archives[p.name]=save(p,out/p.name)
names=['diagnostic-rails-b3','diagnostic-rails-pre-y33-b3','candidate-rail109-b3','flex-baseline-b3','flex-repair-b3','choice-tests-b3','flex-trace-baseline-b3','flex-trace-repair-b3']
repos={}
for name in names:
    repo=root/name;folder=out/'sources'/name;folder.mkdir(parents=True)
    call=lambda *args:subprocess.check_output(['git','-C',str(repo),*args])
    rev=call('rev-parse','HEAD').decode().strip();patch=call('diff','--binary');(folder/'tracked.patch').write_bytes(patch)
    tracked=call('ls-files').decode().splitlines();changed=call('diff','--name-only').decode().splitlines();untracked=call('ls-files','--others','--exclude-standard').decode().splitlines()
    assert all(p.startswith('src/point_add/') for p in changed+untracked)
    protected={}
    for rel in tracked:
        if rel.startswith('src/point_add/'):continue
        b=(repo/rel).read_bytes();assert b==call('show',rev+':'+rel),(name,rel);protected[rel]=sha(b)
    for rel in untracked:save(repo/rel,folder/rel)
    stream=repo/'ops.bin'
    repos[name]={'revision':rev,'patch_sha256':sha(patch),'changed':changed,'untracked':untracked,'protected_unchanged':True,'protected_sha256':protected,
        'point_add_sha256':{rel:sha((repo/rel).read_bytes()) for rel in tracked+untracked if rel.startswith('src/point_add/')},
        'stream_sha256':sha(stream.read_bytes()) if stream.exists() else None,'qualified_score':None}
exits={p.name:int(p.read_text().strip()) for p in root.glob('*.exit')}
for name in ['trace.exit','trace-v2.exit','flex.exit','known.exit','choice-tests.exit','flex-trace.exit']:assert exits[name]==0,(name,exits)
assert exits['candidate.exit']==101
binary={str(p.relative_to(root)):sha(p.read_bytes()) for p in (root/'test-target/release/deps').glob('build_circuit-*') if p.is_file() and os.access(p,os.X_OK)}
old=root.parent/'arithmetic-repair-20261015';packets={str(p):sha(p.read_bytes()) for p in (old/'packets').glob('*.tsv')}
replay={'binary_sha256':sha((old/'fixed-target/release/product_paired_diagnostic').read_bytes()),'source_sha256':sha((old/'fixed-replay/src/main.rs').read_bytes())}
save(old/'fixed-replay/src/main.rs',out/'external-replay/main.rs');save(old/'fixed-replay/Cargo.toml',out/'external-replay/Cargo.toml')
fixed={p.name:next((l for l in p.read_text().splitlines() if l.startswith('FIXED_DIAGNOSTIC')),None) for p in root.glob('*.log') if p.name.startswith(('flex-baseline-','flex-repair-','known-'))}
fixed={k:v for k,v in fixed.items() if v}
receipt={'collected_at_utc':datetime.now(timezone.utc).isoformat(),'status':'terminal finite repair research; full candidate incorrect','qualified_score':None,'official_benchmark_run':False,'submission_made':False,
    'limitations':['Pre-Y33 tracing supersedes the provisional offset-based v1 trace.','Fixed replays use source-independent measurement seeds, but measurement events across changed streams are unaligned; phase-count and gate-count deltas are not paired savings.','Known15 contains only fifteen active lanes; its raw simulator total includes inactive lanes and is not a per-shot metric.','Primitive proof covers 43680 small signed inputs and one wide counterexample, not the full rail schedule.'],
    'exit_codes':exits,'repos':repos,'packets':packets,'replay':replay,'primitive_test_binaries':binary,'fixed_replays':fixed,'archives':archives}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
with tarfile.open(root/'evidence.tar.gz','w:gz') as tar:tar.add(out,arcname='evidence')
print(json.dumps({'status':receipt['status'],'repos':len(repos),'exit_codes':exits,'fixed_replays':fixed},indent=2))
