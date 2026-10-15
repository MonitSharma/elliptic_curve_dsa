"""Archive terminal integration, failed instrumentation, and exact phase evidence."""
from pathlib import Path
from datetime import datetime,timezone
import subprocess,hashlib,json,gzip,tarfile,difflib,re
root=Path(__file__).resolve().parent;out=root/'collected';assert not out.exists();out.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest();archives={}
def save(p,rel):
    b=p.read_bytes();q=out/rel;q.parent.mkdir(parents=True,exist_ok=True)
    if len(b)>262144:q=q.with_suffix(q.suffix+'.gz');q.write_bytes(gzip.compress(b,mtime=0))
    else:q.write_bytes(b)
    archives[rel]={'source_sha256':sha(b),'archive_sha256':sha(q.read_bytes()),'bytes':len(b),'path':str(q.relative_to(out))}
exits={p.name:int(p.read_text()) for p in root.glob('*.exit')}
for name in ['run.exit','phase3.exit','bdd-fresh.exit','witness.exit']:assert exits[name]==0,(name,exits)
assert exits['phase.exit']==101 and exits['phase2.exit']==101
assert 'BDD_NATIVE_COUNTEREXAMPLE_VERIFIED=true' in (root/'witness.log').read_text()
for p in sorted(root.iterdir()):
    if p.is_file() and p.suffix in ['.log','.json','.sha256','.patch','.pid','.exit','.py','.sh']:save(p,p.name)
repos={}
for name in ['combined-b3','trace-combined-b3']:
    repo=root/name;call=lambda *a:subprocess.check_output(['git','-C',str(repo),*a])
    rev=call('rev-parse','HEAD').decode().strip();changed=call('diff','--name-only').decode().splitlines();untracked=call('ls-files','--others','--exclude-standard').decode().splitlines()
    assert all(p.startswith('src/point_add/') for p in changed+untracked)
    protected={}
    for rel in call('ls-files').decode().splitlines():
        if not rel.startswith('src/point_add/'):
            b=(repo/rel).read_bytes();assert b==call('show',rev+':'+rel);protected[rel]=sha(b)
    patch=call('diff','--binary');q=out/'sources'/name/'tracked.patch';q.parent.mkdir(parents=True);q.write_bytes(patch)
    for rel in untracked:save(repo/rel,'sources/'+name+'/'+rel)
    stream=repo/'ops.bin';repos[name]={'revision':rev,'patch_sha256':sha(patch),'changed':changed,'untracked':untracked,'protected_unchanged':True,'protected_sha256':protected,'point_add_changes_sha256':{rel:sha((repo/rel).read_bytes()) for rel in changed+untracked},'stream_sha256':sha(stream.read_bytes()),'score':None}
external=[]
for name in ['phase-context','phase-context-v2','phase-context-v3','phase-bdd','phase-bdd-witness']:
    for p in (root/name).rglob('*'):
        if p.is_file():
            rel=str(p.relative_to(root));save(p,rel)
            external.extend(difflib.unified_diff([],p.read_text().splitlines(True),fromfile='/dev/null',tofile='b/'+rel))
(out/'external-crates.patch').write_text(''.join(external))
for p in (root/'packets').glob('*.tsv'):save(p,'packets/'+p.name)
old=root.parent/'arithmetic-repair-20261015'
for name in ['src/main.rs','Cargo.toml','Cargo.lock']:save(old/'fixed-replay'/name,'fixed-replay/'+name)
diagnostics={p.name:[l for l in p.read_text().splitlines() if l.startswith(('FIXED_DIAGNOSTIC','RAIL_SUMMARY','test result:','FULL_PHASE','PHASE_WITNESS','SINGLE_MEASUREMENT','BDD_WITNESS','BDD_NATIVE'))] for p in root.glob('*.log')};diagnostics={k:v for k,v in diagnostics.items() if v}
fixed_sets={family:sorted(map(int,re.findall(r'FINAL_BAD shot=(\d+)',(root/(family+'.log')).read_text()))) for family in ['known15','independent','structured','candidate']}
assert fixed_sets['candidate']==[562,720,2777,3447,8322]
assert fixed_sets['structured']==list(range(0,256,2)) and fixed_sets['independent']==[]
receipt={'collected_at':datetime.now(timezone.utc).isoformat(),'status':'terminal partial arithmetic repair with exact phase counterexample; no resource qualification','score':None,'official_benchmark_run':False,'submission_made':False,'exit_codes':exits,'repos':repos,'fixed_wrong_sets':fixed_sets,'diagnostics':diagnostics,'replay_binary_sha256':sha((old/'fixed-target/release/product_paired_diagnostic').read_bytes()),'external_crates_patch_sha256':sha((out/'external-crates.patch').read_bytes()),'archives':archives,'invalidated_outputs':{'phase-bdd.log':'Shared Cargo target reused the ANF binary; this is not a BDD result. Superseded by isolated bdd-fresh and witness builds.','phase-bdd-tests.log':'Wrong four-test binary reused; not BDD validation. Isolated build passes all five original BDD tests.'},'limitations':['All counts are diagnostics; no qualified Toffoli or product score.','Arithmetic variants have unaligned measurement events.','Fifteen-shot raw gate totals include inactive lanes.','ANF limit is inconclusive; the isolated BDD proves nonzero phase for one fixed zero-slope input, not all inputs.','BDD witness uses the previous square-room stream, not the combined stream.','No universal safe rail envelope or zero-multiplicand circuit repair established.']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
with tarfile.open(root/'evidence.tar.gz','w:gz') as tar:tar.add(out,arcname='evidence')
print(json.dumps({'exit_codes':exits,'repos':len(repos),'artifacts':len(archives),'diagnostics':diagnostics},indent=2))
