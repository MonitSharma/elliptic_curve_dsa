from pathlib import Path
from datetime import datetime,timezone
import gzip,hashlib,json,subprocess,tarfile
root=Path(__file__).resolve().parents[2];a=Path(__file__).parent;ex=a.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def git(*args):return subprocess.check_output(['git','-C',str(root),*args])
assert not git('diff','--cached','--name-only').strip()
r=ex/'breakthrough-borrowed-recycle-final-20261021'
manifest=json.loads((r/'EVIDENCE-MANIFEST.json').read_bytes());receipt=json.loads((r/'PACKAGE-RESULT.json').read_bytes())
assert sha((r/'final-evidence.tar.gz').read_bytes())==receipt['archive_sha256']
hydrated={}
with tarfile.open(r/'final-evidence.tar.gz')as ar:
 assert len(ar.getmembers())==receipt['members']
 for p,h in manifest['files'].items():
  assert not Path(p).is_absolute() and '..'not in Path(p).parts
  data=ar.extractfile(p).read();assert sha(data)==h
  dest=r/p;dest.parent.mkdir(parents=True,exist_ok=True)
  if dest.exists():assert dest.read_bytes()==data,p
  else:dest.write_bytes(data)
  stored=p
  if p.endswith('.jsonl'):
   stored=p+'.gz';(r/stored).write_bytes(gzip.compress(data,mtime=0))
  hydrated[p]={'raw_sha256':h,'stored_as':stored}
(r/'NESTED-HYDRATION.json').write_text(json.dumps({'status':'EVERY_SEALED_MEMBER_HYDRATED_AND_HASH_CHECKED','members':len(hydrated),'files':hydrated},indent=2)+'\n')
official=json.loads((r/'OFFICIAL-RESULT.json').read_bytes());assert official['Q']==1464 and official['T']==746089
state=json.loads((a/'CURRENT-ACTIVE.json').read_bytes());state['at_utc']=datetime.now(timezone.utc).isoformat()
state['latest_official']=official
state['measurement_recycle_3'].update(official_submission='cb2253eb-7318-416b-8c9e-af9a28bda867',official_Q=1467,official_T=746099,official_product=1094527233,scope='Complete unchanged benchmark and official reproduction. Every207 published source and17 protected files byte verified. Historical sealed scope typo retained and disclosed; exact comparator was FFE20.')
state['borrowed_recycle_13']={'status':'OFFICIALLY_REPRODUCED','source_files':207,'protected_files':17,'native':21,'Q':1464,'T':746089,'product':1092274296,'gate_label':'cb2253-borrowed13-final-20261021-v1','gate_batches':32768,'gate_verdict':'PASS','value_failures_both':1151,'failed_batches_both':1166,'dirty_shots':0,'b':0,'c':0,'p':1,'T_delta':-10,'SE':0,'nonce':142,'screens':192,'benchmark_shots':9024,'public_source_revision':official['public_source_revision']}
state['unitary_cache_front']['scope']='Completed all13 exact original-zero donor leases at originalQ1464, own gate and unchanged benchmark PASS, officially reproducedT746089. WiderQ1477 control preserved and retired before any gate.'
state['active_jobs']=[{'where':'smu_server','pid':3278347,'experiment':'breakthrough-public-semantic-nonce-20261021','phase':'Own gatePASS; ascending1..16777216 original exact engine search, lowestPASS. Old6192 retired search remains retired.'},{'where':'local WSL','windows_pid':44284,'experiment':'breakthrough-compact-context-alias-20261021','phase':'Fresh exact alias rules on cached current-public compact-carry streams; fifteen native and24complete protected comparisons per stream; diagnostic only.'}]
state['next_product_front']='Current public exact cap1233-r012 plus fresh114contextcaches is near product threshold; fresh full-prefix aliases now running. Expand predeclared exact carry allocation grid if needed. No witness/round cuts; fresh own gate on frozen final source before any nonce. Global product goal ACTIVE. Approved41 push already fulfilled; newer commits local. Preserve Q692/user edits/chemistry.'
(a/'CURRENT-ACTIVE.json').write_text(json.dumps(state,indent=2)+'\n')
with(a/'LOG.md').open('a',encoding='utf-8')as log:log.write('\n## '+state['at_utc']+'\nOfficialcb2253 Q1467/T746099 then8d704a6b Q1464/T746089 confirmed;207source+17protected bytes each verified. Both complete9024benchmarksPASS; independentT improvement, globalproduct unchanged932057476. Borrowed own32768pairedgatePASS b=c0,p1,dirty0,Tdelta-10 exact; nonce142/192ascending screens, all159sealed evidence members locally verified and158hydrated. Conditional/future/moving/implicit guard research preserved, no newrecords. Fresh compact-context exactalias component running; globalproduct ACTIVE; approved41push alreadydone, newercommitslocal.\n')
addition='''## Official Toffoli improvement · 21 October 2026, 11:50 SGT

The challenge officially reproduced **1,464 qubits × 746,089 rounded mean
executed Toffolis = 1,092,274,296**, with all 9,024 benchmark shots passing, in
[submission 8d704a6b](https://api.ecdsa.fail/api/submissions/8d704a6b-659c-4d67-9bd0-f6862de9f617).
This follows the official Q1467/T746099 result and saves another **10 Toffolis
and 3 qubits**. All 207 published source files and 17 protected files match
the verified source. Attribution: **GPT-6 sol / Codex**.

Fresh public records confirm the independent Toffoli minimum. The global
product remains **932,057,476**; promotion was declined because that product
is lower. Its improvement remains the active objective, with Q692 preserved.

[Source and statistical disclosures](experiments/breakthrough-borrowed-recycle-final-20261021/SUBMISSION-NOTE.md) ·
[Official source verification](experiments/breakthrough-borrowed-recycle-final-20261021/PUBLIC-SOURCE-VERIFICATION.json) ·
[Evidence verification](experiments/breakthrough-borrowed-recycle-final-20261021/NESTED-HYDRATION.json)

'''
prefixes={'README.md':addition,'docs/research-plan.md':'''## 21 October 2026: two further official Toffoli improvements

Official cb2253 Q1467/T746099, then 8d704a6b Q1464/T746089, complete unchanged
9024-shot benchmarks PASS, all207 source/17 protected files exact. Own final
borrowed13 gate32768x64 versus exactcb2253:1151 value failures each,1166 failed
batches each, dirty0, b=c0,p1, exactTdelta-10/SE0. Nonce142,192ascending screens,
lowestPASS; all159sealed evidence members independently verified,158hydrated.
Fresh03:50UTC1719records confirm T minimum; globalproduct932057476 unchanged.
Conditional donors21native/full48, future-target18/full48, moving18/full48
and improvedmoving18/full48, implicitguardV2 native10/full48 preserved. These
are component research only, with no additional record. Wider1477 control is
retired before gate. Current compactcarryQ1233+114freshcontext caches is near
product threshold; fresh exact fullprefix alias qualification now running.
Globalproduct objective ACTIVE; newerrootcommits local, approved41push done.
Preserve Q692, prior verdicts, original retired6192search and all user edits.

'''}
prefix_staged=[]
for p,prefix in prefixes.items():
 original=(root/p).read_text(encoding='utf-8')
 if not original.startswith(prefix):(root/p).write_text(prefix+original,encoding='utf-8')
 baseline=git('show','HEAD:'+p);blob=subprocess.check_output(['git','-C',str(root),'hash-object','-w','--stdin'],input=prefix.encode()+baseline).decode().strip()
 subprocess.run(['git','-C',str(root),'update-index','--cacheinfo','100644,'+blob+','+p],check=True);prefix_staged.append(p)
names=['breakthrough-recycle-final-20261021','breakthrough-borrowed-recycle-20261021','breakthrough-borrowed-recycle-development-20261021','breakthrough-borrowed-recycle-final-20261021','breakthrough-borrowed-recycle-final-gate-20261021','breakthrough-borrowed-recycle-finished-20261021','breakthrough-borrowed-recycle-nonce-20261021','breakthrough-recycle-unitary-finished-20261021','breakthrough-conditional-borrowed-recycle-20261021','breakthrough-future-target-recycle-20261021','breakthrough-moving-recycle-20261021','breakthrough-moving-recycle-v2-20261021','breakthrough-implicit-classical-guards-20261021','breakthrough-implicit-classical-guards-v2-20261021','breakthrough-compact-context-alias-20261021']
paths=[]
for name in names:
 d=ex/name
 if not d.exists():continue
 fp=d/'SOURCE-FREEZE.json'
 if fp.exists()and(d/'local-tool').exists():
  f=json.loads(fp.read_bytes());files=f.get('tool_source_files',{})
  if files and all((d/'local-tool'/p).is_file()for p in files):
   assert all(sha((d/'local-tool'/p).read_bytes())==h for p,h in files.items())
   with tarfile.open(d/'preserved-tool-source.tar.gz','w:gz')as ar:
    for p in sorted(files):ar.add(d/'local-tool'/p,arcname=p,recursive=False)
 for p in d.rglob('*'):
  rel=p.relative_to(d)
  if any(x in rel.parts for x in ['candidate','local-tool','target','__pycache__']):continue
  if p.name.endswith('.ops.bin')or p.name.endswith('.jsonl')or p.name in ['ops.bin','normalized-value-ir.bin.zst','final-evidence.tar.gz']:continue
  if p.is_file()and p.stat().st_size<20_000_000:paths.append(p.relative_to(root).as_posix())
for p in a.iterdir():
 if p.suffix in ['.py','.rs','.json']and p.name not in ['ROOT-CHECKPOINT.json']:paths.append(p.relative_to(root).as_posix())
paths.append((a/'LOG.md').relative_to(root).as_posix())
assessment=ex/'breakthrough-assessment-20261020';paths.append((assessment/'LATEST.json').relative_to(root).as_posix())
for d in ['20261021T025420Z','20261021T035053Z']:
 sd=assessment/'snapshots'/d
 if sd.exists():paths.extend(p.relative_to(root).as_posix()for p in sd.rglob('*')if p.is_file())
latest=json.loads((assessment/'LATEST.json').read_bytes());sd=assessment/latest['snapshot']
paths.extend(p.relative_to(root).as_posix()for p in sd.rglob('*')if p.is_file())
paths=sorted(set(paths));subprocess.run(['git','-C',str(root),'add','-f','--pathspec-from-file=-','--pathspec-file-nul'],input=b'\0'.join(p.encode()for p in paths)+b'\0',check=True)
assert set(git('diff','--cached','--name-only').decode().splitlines())<=set(paths+prefix_staged)
subprocess.run(['git','-C',str(root),'commit','-q','-m','Preserve two official Toffoli improvements and exact borrowed-wire evidence'],check=True)
print(git('rev-parse','HEAD').decode().strip())
