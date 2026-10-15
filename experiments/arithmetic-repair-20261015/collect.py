"""Archive bounded evidence, exact source diffs, protected-file checks and terminal status."""
from pathlib import Path
from datetime import datetime, timezone
import gzip
import hashlib
import json
import re
import subprocess
import tarfile

root=Path(__file__).resolve().parent
out=root/'collected'
assert not out.exists()
out.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest()
def command(*args):return subprocess.check_output(args,text=True)
def save(path,target):
    raw=path.read_bytes();target.parent.mkdir(parents=True,exist_ok=True)
    if len(raw)>262144:
        target=target.with_suffix(target.suffix+'.gz');target.write_bytes(gzip.compress(raw,mtime=0))
    else:target.write_bytes(raw)
    return {'source_sha256':sha(raw),'source_bytes':len(raw),'archive_path':str(target.relative_to(out)),'archive_sha256':sha(target.read_bytes())}

receipts={}
for path in sorted(root.iterdir()):
    if path.is_file() and path.suffix in ['.log','.json','.sha256','.patch','.pid','.exit','.rs','.py','.sh']:
        receipts[path.name]=save(path,out/path.name)
repos={}
for name in ['diagnostic-b3','diagnostic-reset-b3','diagnostic-payload-b3','pool-observer-b3',
             'candidate-fold104-b3','diagnostic-fold104-b3','candidate-fold104-unbound-b3']:
    repo=root/name;folder=out/'sources'/name;folder.mkdir(parents=True)
    revision=command('git','-C',str(repo),'rev-parse','HEAD').strip()
    patch=subprocess.check_output(['git','-C',str(repo),'diff','--binary'])
    (folder/'tracked.patch').write_bytes(patch)
    tracked=command('git','-C',str(repo),'ls-files').splitlines()
    changed=command('git','-C',str(repo),'diff','--name-only').splitlines()
    untracked=command('git','-C',str(repo),'ls-files','--others','--exclude-standard').splitlines()
    assert all(p.startswith('src/point_add/') for p in changed+untracked),(name,changed,untracked)
    protected={}
    for relative in tracked:
        if relative.startswith('src/point_add/'):continue
        original=subprocess.check_output(['git','-C',str(repo),'show',f'{revision}:{relative}'])
        current=(repo/relative).read_bytes()
        assert original==current,(name,relative,'protected file changed')
        protected[relative]=sha(current)
    source={p:sha((repo/p).read_bytes()) for p in tracked+untracked if p.startswith('src/point_add/')}
    for relative in untracked:save(repo/relative,folder/relative)
    stream=repo/'ops.bin'
    repos[name]={'revision':revision,'changed_files':changed,'untracked_files':untracked,
                 'patch_sha256':sha(patch),'point_add_sha256':source,'protected_sha256':protected,
                 'protected_unchanged':True,'stream_sha256':sha(stream.read_bytes()) if stream.exists() else None,
                 'qualified_score':None}
for relative in ['src/main.rs','src/bin/compare_raw.rs','src/bin/compare_raw_v2.rs','src/bin/local_proof.rs','src/proof_kernel.rs','Cargo.toml','Cargo.lock','rust-toolchain']:
    path=root/'fixed-replay'/relative
    if path.exists():receipts['fixed-replay/'+relative]=save(path,out/'replay-source'/relative)
packets={p.name:{'sha256':sha(p.read_bytes()),'shots':sum(1 for _ in p.open())} for p in (root/'packets').glob('*.tsv')}
exits={p.name:int(p.read_text().strip()) for p in root.glob('*.exit')}
for name in ['run.exit','reset.exit','payload.exit','pool.exit','raw-candidate.exit','compare.exit','compare-v2.exit','proof.exit','unbound.exit']:
    assert exits[name]==0,(name,exits[name])
assert exits['candidate.exit']==101
assert exits['fixed.exit']==1
pairing=[line for line in (root/'compare-v2.log').read_text().splitlines() if line.startswith(('RAW_LOCALITY','PAIRED_REPAIR','PHASE_CHANGE','CHANGED_CORRECTNESS'))]
fixed={family:next(line for line in (root/f'unbound-{family}.log').read_text().splitlines() if line.startswith('FIXED_DIAGNOSTIC')) for family in ['independent','structured','candidate']}
proof=[line for line in (root/'proof.log').read_text().splitlines() if line.startswith(('PROOF_SCOPE','LOCAL_ALLMR_PASS','NATIVE_SUFFIX_VALUE_PASS'))]
resets=[line for line in (root/'reset-trace.log').read_text().splitlines() if line.startswith('FIRST_NONZERO_RESET family=candidate')]
summary={'collected_at_utc':datetime.now(timezone.utc).isoformat(),'status':'partial arithmetic repair; known independent/structured failures remain',
         'qualified_score':None,'official_benchmark_run':False,'submission_made':False,
         'note':'The preserved candidate packet is replayed on changed source; it is not this source\'s official hash-derived packet.',
         'terminal_exit_codes':exits,'packets':packets,'repos':repos,'pairing':pairing,'fixed_replay':fixed,'local_proof':proof,
         'nonzero_resets_on_candidate_packet':resets,'archives':receipts}
(out/'receipt.json').write_text(json.dumps(summary,indent=2)+'\n')
with tarfile.open(root/'evidence.tar.gz','w:gz') as tar:tar.add(out,arcname='evidence')
print(json.dumps({'status':summary['status'],'qualified_score':None,'exits':exits,'pairing':pairing,'local_proof':proof,'fixed_replay':fixed},indent=2))
