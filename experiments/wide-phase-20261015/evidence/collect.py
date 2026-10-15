"""Preserve source attribution, terminal cleanup experiment, and component proof."""
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
for name in ['origin.exit']:assert exits[name]==0,(name,exits)
assert (root/'origin-equality.log').read_text().strip()=='BYTE_IDENTICAL_STREAM=true'
for p in sorted(root.iterdir()):
 if p.is_file() and p.suffix in ['.log','.json','.sha256','.patch','.pid','.exit','.py','.sh','.rs']:save(p,p.name)
repos={}
for name in ['origin-b3']:
 repo=root/name;call=lambda *a:subprocess.check_output(['git','-C',str(repo),*a]);rev=call('rev-parse','HEAD').decode().strip()
 changed=call('diff','--name-only').decode().splitlines();untracked=call('ls-files','--others','--exclude-standard').decode().splitlines();assert all(p.startswith('src/point_add/') for p in changed+untracked)
 protected={}
 for rel in call('ls-files').decode().splitlines():
  if not rel.startswith('src/point_add/'):
   b=(repo/rel).read_bytes();assert b==call('show',rev+':'+rel);protected[rel]=sha(b)
 patch=call('diff','--binary');q=out/'sources'/name/'tracked.patch';q.parent.mkdir(parents=True);q.write_bytes(patch)
 for rel in untracked:save(repo/rel,'sources/'+name+'/'+rel)
 stream=repo/'ops.bin';repos[name]={'revision':rev,'patch_sha256':sha(patch),'changed':changed,'untracked':untracked,'protected_unchanged':True,'protected_sha256':protected,'point_add_changes_sha256':{rel:sha((repo/rel).read_bytes()) for rel in changed+untracked},'stream_sha256':sha(stream.read_bytes()) if stream.exists() else None,'score':None}
external=[];prior=root.parent/'repair-integration-20261015'
for p in (prior/'phase-bdd-witness').rglob('*'):
 if p.is_file():
  rel='phase-bdd-witness/'+str(p.relative_to(prior/'phase-bdd-witness'));save(p,rel);external.extend(difflib.unified_diff([],p.read_text().splitlines(True),fromfile='/dev/null',tofile='b/'+rel))
(out/'external-crates.patch').write_text(''.join(external))
old=root.parent/'arithmetic-repair-20261015'
for p in (old/'packets').glob('*.tsv'):save(p,'packets/'+p.name)
for rel in ['src/main.rs','Cargo.toml','Cargo.lock']:save(old/'fixed-replay'/rel,'fixed-replay/'+rel)
diagnostics={p.name:[l for l in p.read_text().splitlines() if l.startswith(('FIXED_DIAGNOSTIC','TERMINAL_EXACT','TERMINAL_UNSEEDED','CARRY_STATE','CARRY_COMPARE','CARRY_OBSERVATION','Y42_FRESH_RETURNED','HEO_TOTAL','test result:','FULL_PHASE','PHASE_WITNESS','SINGLE_MEASUREMENT','BDD_WITNESS','BDD_NATIVE','PHASE_ORIGIN','PHASE_SOURCE'))] for p in root.glob('*.log')};diagnostics={k:v for k,v in diagnostics.items() if v}
fixed_sets={}
receipt={'collected_at':datetime.now(timezone.utc).isoformat(),'status':'terminal gate-inert source observation; not a candidate benchmark','score':None,'official_benchmark_run':False,'submission_made':False,'exit_codes':exits,'repos':repos,'source_trace_byte_identical':True,'fixed_wrong_sets':fixed_sets,'diagnostics':diagnostics,'witness_binary_sha256':sha((prior/'witness-target/release/product_paired_diagnostic').read_bytes()),'replay_binary_sha256':sha((old/'fixed-target/release/product_paired_diagnostic').read_bytes()),'external_crates_patch_sha256':sha((out/'external-crates.patch').read_bytes()),'archives':archives,'limitations':['Fixed-input diagnostics only; no qualified resource result.','Candidate arithmetic changes measurement events; raw count differences are not aligned savings.','A full-stream all-measurement audit here covers one fixed zero-slope input, not every input.','Allocator tests establish bookkeeping invariants, not quantum cleanliness; fixed replay checks dirty ancillas separately.','Other approximate comparisons, rail failures and zero-multiplicand preconditions remain.']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
with tarfile.open(root/'evidence.tar.gz','w:gz') as tar:tar.add(out,arcname='evidence')
print(json.dumps({'artifacts':len(archives),'repos':len(repos),'exit_codes':exits,'diagnostics':diagnostics},indent=2))
