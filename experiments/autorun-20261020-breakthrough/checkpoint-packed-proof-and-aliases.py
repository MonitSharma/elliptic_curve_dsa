import gzip,hashlib,json,subprocess,tarfile
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[2];a=Path(__file__).parent;ex=a.parent;sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def git(*args,input=None):return subprocess.check_output(['git','-C',str(root),*args],input=input)
assert not git('diff','--cached','--name-only').strip()
dirs=['breakthrough-reference-frame-profile-20261021','breakthrough-current-product-census-anf-shadow-20261021','breakthrough-current-product-census-anf-shadow-v2-20261021','breakthrough-original-reset-cache-20261021','breakthrough-global-quantum-alias-20261021','breakthrough-global-quantum-alias-v2-20261021','breakthrough-global-quantum-alias-v3-20261021','breakthrough-global-quantum-pair-alias-20261021','breakthrough-global-quantum-pair-alias-v2-20261021']
excluded={'local-tool','candidate','target','__pycache__'}
for name in dirs:
 r=ex/name;f=json.loads((r/'SOURCE-FREEZE.json').read_bytes());names=f.get('tool_source_files',f.get('source_files',{}));assert all(sha(r/'local-tool'/n)==h for n,h in names.items());archive=r/'preserved-tool-source.tar.gz'
 if not archive.exists():
  with tarfile.open(archive,'w:gz')as ar:
   for n in sorted(names):ar.add(r/'local-tool'/n,arcname=n,recursive=False)
 with tarfile.open(archive)as ar:
  assert {m.name for m in ar.getmembers()}==set(names)
  for m in ar.getmembers():assert m.isfile()and hashlib.sha256(ar.extractfile(m).read()).hexdigest()==names[m.name]
 (r/'PRESERVED-TOOL-SOURCE.json').write_text(json.dumps({'files':names,'archive_sha256':sha(archive)},indent=2)+'\n')
 files={}
 for p in r.rglob('*'):
  rel=p.relative_to(r)
  if any(x in excluded for x in rel.parts):continue
  if not p.is_file()or p.name.endswith('ops.bin')or p.name=='LOCAL-CHECKPOINT-MANIFEST.json':continue
  assert p.stat().st_size<20_000_000;files[rel.as_posix()]=sha(p)
 (r/'LOCAL-CHECKPOINT-MANIFEST.json').write_text(json.dumps({'files':files,'scope':'Frozen completed or explicitly failed/pretest source-bound research evidence. No new quantum resource record, final gate, nonce screen or challenge submission.'},indent=2)+'\n')
proof=json.loads((ex/'breakthrough-current-product-census-anf-shadow-v2-20261021/RESULT.json').read_bytes());assert proof['shadow']['fully_known_output_shots']==32768 and proof['shadow']['certified_wrong_shots']==54 and proof['nonce_rejections']==0
latest=json.loads((ex/'breakthrough-assessment-20261020/LATEST.json').read_bytes());snap=ex/'breakthrough-assessment-20261020'/latest['snapshot'];snapshots=[snap,ex/'breakthrough-assessment-20261020/snapshots/20261020T235217Z']
for s in snapshots:
 raw=s/'public-submissions.json'
 if raw.exists():raw.with_suffix('.json.gz').write_bytes(gzip.compress(raw.read_bytes(),mtime=0))
 (s/'SNAPSHOT-MANIFEST.json').write_text(json.dumps({'files':{p.name:sha(p)for p in s.iterdir()if p.is_file()and p.name not in ['SNAPSHOT-MANIFEST.json','public-submissions.json']},'scope':'Raw public API response retained as gzip; only official evaluated records enter leader comparisons.'},indent=2)+'\n')
active=ex/'breakthrough-quantum-sharing-profile-20261021';done=(active/'run.exit').exists();active_summary='DONE'if done else'RUNNING_READONLY_NO_SCORE'
state=json.loads((a/'CURRENT-ACTIVE.json').read_bytes());state.update(at_utc=datetime.now(timezone.utc).isoformat(),latest_public_snapshot=snap.relative_to(root).as_posix(),active_jobs=[]if done else[{'environment':'local WSL Ubuntu','directory':active.name,'windows_pid':27672,'purpose':'Read-only exact quantum-function sharing profile, native5PASS; count distinct helper functions and conservative copy-on-write pressure. No emitted allocator or qubit record. Inspect run.exit before any restart.'}],current_parent_census_shadow={'status':'COMPLETE_PASS_VERIFIER_RESEARCH_ONLY','batches':512,'shots':32768,'native_controls':39,'fresh_full_protected_arbitrary_comparisons':24,'fully_known_outputs':32768,'stored_and_certified_value_failures':54,'false_rejections':0,'output_hash_mismatches':0,'unknown_outputs':0,'seconds':106.727310831,'original_FS_production_filter_qualified':False,'nonce_screens':0,'nonce_rejections':0},classical_reference_frame_result='Native6/fullbothparentsCOMPLETE; projectedpeak1234/1464, no width saving. Currentpublic0nonlinear terms eliminated; retired, no emitter.',original_reset_cache_result='Native11PASS, exactpublic original source yields0pair nominees and0delayed leases, canonical output exactlyparent3000fc. No insertedmeasurements/pointinputs/gate/nonce/benchmark; retire currentparent front.',quantum_alias_result='Native15PASS/fullcurrentpublic+ffe20complete. One-wire exact quantum alias adds0new rewrites: public onlypreviousoneCCXtoCX, ffe20none. Firstpretestvariant and14of15native missed-guard proof retained. Input-copysetuprepair retained, no inputsource change.',quantum_pair_alias_result='Native18PASS/fullcurrentpublic+ffe20complete. Two-wire exact lookup adds0new rewrites on both; onlypreviouspubliconeCCXtoCX. Prior17of18native missed guarded-complement proof retained. No new circuit/gate/nonce/benchmark.',next_product_front='Check read-only exact quantum-function sharing pressure before designing reversible compression/copy-on-write allocator. If no peak margin, retire. Packed value proof now qualifies ALL32768preserved currentparent points; next verifier step must reproduce ORIGINAL_FS transcripts from previously screened fixed controls before production rejection. No retired nonce search may resume.',new_official_summary='No further official submission in this cycle. Our prior officialffe20 Q1464/T746112 remains fresh publicT minimum. Globalproduct1829 Q1234/T755314/932057476; width669. Product goal ACTIVE_UNFINISHED. Human-approved exact41f769ec pushed previously; newer localcommits NOT authorized for push.')
if done:state['quantum_sharing_profile']=json.loads((active/'RESULT.json').read_bytes())
(a/'CURRENT-ACTIVE.json').write_text(json.dumps(state,indent=2)+'\n')
addition='''## 21 October 2026: 32,768-point exact value proof qualification

Fresh00:40UTC1717publicrecords unchanged: our officialffe20 Q1464/T746112,
globalproduct1829 Q1234/T755314/932057476, width669. Product objective ACTIVE.
No new benchmark/finalgate/nonce screen/challenge submission in this cycle.

Exact CURRENTpublic source/normalizedIR, unchanged fast boundedANF core:
native39PASS (37existing+2independent transcript/hash controls), fresh24protected
arbitrary-input comparisons. Regenerated ALL512x64 preserved development inputs
from original label/domain/LElength/LEbatch/scalar order; checked every skip
count and recorded failure scalar. Every one of32768outputpoints fully known,
every recorded independent protected/SIMD target hash identical. All54recorded
value failures certified; unknown0, false rejection0, output mismatch0.
106.727310831sec including point generation. No new census or pastgate rejudged,
no nonce screened/rejected; originalFS production qualification still required.
Compile-only scalar type inference failure preserved; V2 uses exact typed parser.

Read-only classical-reference frame native6/fullbothparents complete: projected
peak1234/1464, no width saving; no emitter. Original-reset cache native11/full
publiccomplete:0pairnominees/0leases, exactparent canonical3000fc. Retire both.
One-wire quantum alias native15 and two-wire XORalias native18/fullpublic+exact
latestffe20 streams complete: no additional rewrite. Public onlypriorCCXtoCX,
latestT none. Guarded-complement missed-proof native failures and input-copy
setup repair preserved; never source/point/gate tuning. No quantum result.

Next read-only quantum-value-sharing profile native5PASS: count distinct helper
functions and conservative copy-on-write pressure before considering a reversible
compression allocator. No projected count is an achieved width/record. Original
measurement phase/RNG, guards and full protected qualification remain mandatory.
Preserve Q692 and every sealed old failure/verdict. Chemistry/unrelatedjobs intact.
Exact approved41f769ec push previously completed; newer commits remain local.

'''
for rel in ['docs/research-plan.md','docs/AGENT_HANDOFF.md']:
 p=root/rel;data=addition.encode()
 if not p.read_bytes().startswith(data):p.write_bytes(data+p.read_bytes())
 blob=git('hash-object','-w','--stdin',input=data+git('show','HEAD:'+rel)).decode().strip();mode=git('ls-tree','HEAD','--',rel).decode().split(' ',1)[0];subprocess.run(['git','-C',str(root),'update-index','--add','--cacheinfo',mode+','+blob+','+rel],check=True)
with(a/'LOG.md').open('a',encoding='utf-8')as log:log.write('\n'+addition)
scripts=['reference-frame-profile.rs','prepare-reference-frame-profile.py','value-anf-census-shadow.rs','prepare-census-anf-shadow.py','prepare-census-anf-shadow-v2.py','delayed-reset-cache.rs','prepare-delayed-reset-cache.py','global-quantum-alias-tests.rs','prepare-global-quantum-alias.py','prepare-global-quantum-alias-v2.py','prepare-global-quantum-alias-v3.py','repair-quantum-alias-input-copy.py','prepare-global-quantum-pair-alias.py','prepare-global-quantum-pair-alias-v2.py','quantum-sharing-profile.rs','prepare-quantum-sharing-profile.py','checkpoint-packed-proof-and-aliases.py','CURRENT-ACTIVE.json','LOG.md']
paths=['experiments/'+n for n in dirs]+['experiments/autorun-20261020-breakthrough/'+n for n in scripts]+[s.relative_to(root).as_posix()for s in snapshots]+['experiments/breakthrough-assessment-20261020/LATEST.json']
if done:paths.append(active.relative_to(root).as_posix())
else:paths.extend((active/n).relative_to(root).as_posix()for n in ['.gitignore','.gitattributes','SOURCE-FREEZE.json','discover.rs','run.py','run-local.sh','PLAN.md','tests.log','build.log'])
subprocess.run(['git','-C',str(root),'add','--',*paths,':!**/public-submissions.json'],check=True)
staged=git('diff','--cached','--name-only').decode().splitlines();allowed=paths+['docs/research-plan.md','docs/AGENT_HANDOFF.md'];assert all(any(p==q or p.startswith(q+'/')for q in allowed)for p in staged);assert not any('/local-tool/'in p or p.endswith('ops.bin')or p.endswith('.jsonl')for p in staged)
subprocess.run(['git','-C',str(root),'commit','-q','-m','Qualify current-parent packed value proof on all 32768 preserved inputs'],check=True);print(git('rev-parse','HEAD').decode().strip());print('sharing profile',active_summary)
