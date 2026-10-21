import gzip,hashlib,json,subprocess,tarfile
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[2];a=Path(__file__).parent;ex=a.parent
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def git(*args,input=None):return subprocess.check_output(['git','-C',str(root),*args],input=input)
assert not git('diff','--cached','--name-only').strip()
dirs=['breakthrough-current-product-normalized-aig-20261020','breakthrough-word-value-audit-20261020','breakthrough-normalized-anf-word-audit-20261020','breakthrough-current-product-anf-audit-20261020','breakthrough-fast-current-product-anf-20261020','breakthrough-fast-current-product-anf-v2-20261020','breakthrough-public-product-generic-repeat-20261020','breakthrough-public-semantic-development-20261020','breakthrough-de8-repeat-finished-20261020','breakthrough-de8-repeat-finished-development-20261020','breakthrough-de8-repeat-final-gate-20261020','breakthrough-de8-repeat-nonce-20261020','breakthrough-de8-repeat-final-20261020','breakthrough-de8-second-cache-20261020','breakthrough-de8-generic-repeat-v3-20261020','breakthrough-de8-generic-development-20261020']
excluded={'local-tool','candidate','prepared-source','target','__pycache__','observer','tool-source'}
skip_names={'final-evidence.tar.gz','evidence.tar.gz','normalized-value-ir.bin.zst','LOCAL-CHECKPOINT-MANIFEST.json'}
for name in dirs:
 r=ex/name;(r/'.gitattributes').write_text('* -text\n');p=r/'.gitignore';prior=p.read_text()if p.exists()else''
 for line in [*(x+'/'for x in sorted(excluded)),'*.ops.bin','*.cnf','*.drat','*.jsonl','normalized-value-ir.bin.zst','final-evidence.tar.gz','evidence.tar.gz']:
  if line not in prior.splitlines():prior+=line+'\n'
 p.write_text(prior)
 for p in r.glob('*.jsonl'):p.with_suffix('.jsonl.gz').write_bytes(gzip.compress(p.read_bytes(),mtime=0))
 f=json.loads((r/'SOURCE-FREEZE.json').read_bytes())if(r/'SOURCE-FREEZE.json').exists()else{}
 names=f.get('tool_source_files',f.get('source_files',{}))
 if(r/'local-tool').is_dir()and names and all((r/'local-tool'/n).is_file()for n in names):
  assert all(sha(r/'local-tool'/n)==h for n,h in names.items())
  archive=r/'preserved-tool-source.tar.gz'
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
  if not p.is_file()or p.suffix in ['.cnf','.drat','.jsonl']or p.name.endswith('ops.bin')or p.name in skip_names:continue
  assert p.stat().st_size<20_000_000,(name,rel,p.stat().st_size);files[rel.as_posix()]=sha(p)
 (r/'LOCAL-CHECKPOINT-MANIFEST.json').write_text(json.dumps({'files':files,'scope':'Source-bound completed evidence. Only ffe20 is an officially evaluated new quantum result; verifier/development/projection counts are not records. No gate verdict rerun.'},indent=2)+'\n')
final=ex/'breakthrough-de8-repeat-final-20261020';official=json.loads((final/'OFFICIAL-RESULT.json').read_bytes());assert official['T']==746112
assert json.loads((final/'NESTED-HYDRATION.json').read_bytes())['verified_members']==239
gate=json.loads((ex/'breakthrough-de8-repeat-final-gate-20261020/GATE-RESULT.json').read_bytes());assert gate['verdict']=='FAILURE_RATE_GATE_PASS'
latest=json.loads((ex/'breakthrough-assessment-20261020/LATEST.json').read_bytes());snap=ex/'breakthrough-assessment-20261020'/latest['snapshot']
state=json.loads((a/'CURRENT-ACTIVE.json').read_bytes());state.update(at_utc=datetime.now(timezone.utc).isoformat(),official_latest=official,new_official_summary='Official ffe20 Q1464/T746112,2 fewer T at unchanged width, all9024PASS. Promotion declined solely because global product remains lower. Independent T record; global product goal ACTIVE.',global_product_goal_status='ACTIVE_UNFINISHED',active_jobs=[{'environment':'local WSL Ubuntu bounded read-only analysis','directory':'breakthrough-reference-frame-profile-20261021','purpose':'Six native algebra controls then exact classical-reference/deviation support lifetime projection on public1829/de8. No emitted circuit, scored result, gate or nonce. Inspect run.exit before relaunch.'}],active_submission=None,latest_public_snapshot=snap.relative_to(root).as_posix(),local_evidence={'archive_sha256':'c6ae275037efb55a5dadc6bd62f7a4045144b6d39b1b8664cc1cbf40b51049f1','members':239,'source_files':206,'protected_files':17,'scope':'Every immutable evidence/source member independently verified locally; official published206pointAdd/17protected Git-object bytes match final validated source.'},repeat_final_gate=gate,next_product_front='Read-only exact classical reference frame q=B XOR delta; B is original replay with quantum inputszero, D encloses quantum dependence. Project whether classically known nonzero helpers can be removed and nonlinear terms lowered before investing in exact phase/guard/RNG-preserving emitter. No circuit or record yet.',packed_value_proof='Current exact public1829 normalized numericIR has309remaining CRNG atoms. Unchanged qualified ANF tool certifies128preserved failures, leaves64passingcontrols unrejected, all512bitsknown for192inputs,33fresh protected comparisons. Faster inlineconstant representation native37+33protected alsoPASS,.132..153s/64inputs. Verifier research only; originalFS production filtering NOT qualified or used.',negative_verifier_front='Word DAG native34/cache24protectedPASS but all3groups hit1mnode cap before fixed-point fullcomparison: INCONCLUSIVE, no certificate. First inlineconstant attempt stopped pre-test for bound-policy mismatch; V2 corrects bound, original attempt retained.',public_semantic_development='One exactCCXtoCX, fresh512x64/source development delta-.49945068359375 T, SE.00281224955550836; same63value/50phase/dirty0/78failedbatches, alltarget/otherhashesequal. Component only, no finished candidate/finalgate/nonce/benchmark.',preservation='Original failures and all sealed verdicts preserved; no chemistry/unrelated workloads changed. Newer commits remain local; exact approved41f769ec push completed, approval does not cover newer HEAD.')
(a/'CURRENT-ACTIVE.json').write_text(json.dumps(state,indent=2)+'\n')
addition='''## 21 October 2026: official T746112 and current-parent exact proof port

Official submission ffe20d35-ecb7-47da-9dde-1b8d80ffde60 reproduced Q1464 /
T746112 / product1092307968, all9024shotsPASS; two fewer rounded T than de8.
Published source4033714f, all206pointAdd+17protected file bytes match final
validated774785d2. Attribution GPT-6 sol/Codex. Promotion declined solely because
global product932057476 remains lower. Fresh23:52UTC public1717records confirm
independentT minimum; product1829 Q1234/T755314, width669. Global product ACTIVE.

Sole gatecache-repeat-generic-final-20261020-v1:32768x64/source PASS,1133value
shots each, dirty0, candidate/parent1175/1165failedbatches, b21/c11, one-sided
exactMcNemarp=.055092082591727376, candidate5.055999755859375failedbatches/packet.
Disclosed nonce261, ascending1..320 screens, passes261/291; choose lowest, never
byToffolis. Qualified full-state/RNG controls and unchanged benchmarkPASS.
All239archive members reverified locally,199nestedmembers hydrated byteexact.
Archivec6ae2750 retained on disk/server; individual sourcearchives/evidence saved.

Current public1829 exact normalizedIR/AIG port unchangednative29/fresh27protected
PASS:309CRNGnodes, all512fixedoutputbitsconstant,234wrongbits/emptyclauses.
PackedANF unchangednative37/fresh33protected:all128frozenfailures certified and
64passingcontrols leftunrejected, all512bitsknown for192inputs. Inlineconstant
representationV2 native37/fresh33protected alsoPASS,.132..153s/64 vs.291..298s.
These are verifier results only; no production nonce filtering/rejection used.
WordDAG3groups hit1mnode cap:INCONCLUSIVE; pretestinlineconstant policy failure
retained, V2corrects same8totalterm bound. No pastgate verdict rerun or upgraded.

Public semantic oneCCXtoCX development512x64/source:delta-.49945068359375 T,
SE.00281224955550836, same63value/50phase/dirty0/78failedbatches; everytarget and
otherregisterhash agrees. Component only, no finalgate/nonce/benchmark. Generic
publicrepeat has no static resource gain. New read-only classical reference
q=B XOR delta/support lifetime profile is running, native6PASS; no emitted
circuit or projected result is a score. Exact phase/guard/RNG-preserving emission
and full independent pipeline required for any next candidate. PreserveQ692.

Exact human-approved41f769ec push completed; newer commits stay local. Preserve
preexisting root/submodule edits, original failures, chemistry and unrelatedjobs.

'''
readme='''## Official Toffoli improvement · 21 October 2026, 07:52 SGT

The challenge officially reproduced **1,464 qubits × 746,112 rounded mean
executed Toffolis = 1,092,307,968**, all 9,024 shots passing, in
[submission ffe20d35](https://api.ecdsa.fail/api/submissions/ffe20d35-ecb7-47da-9dde-1b8d80ffde60).
This saves **2 further Toffolis at unchanged width**. All 206 published source
files and 17 protected files match the validated source. Attribution:
**GPT-6 sol / Codex**.

The fresh 23:52 UTC records confirm the independent Toffoli minimum. The global
product remains **932,057,476**; promotion was declined because that product is
lower. The global product objective remains active, and Q692 evidence is preserved.

[Source and disclosures](experiments/breakthrough-de8-repeat-final-20261020/SUBMISSION-NOTE.md) ·
[Official source verification](experiments/breakthrough-de8-repeat-final-20261020/PUBLIC-SOURCE-VERIFICATION.json) ·
[Evidence verification](experiments/breakthrough-de8-repeat-final-20261020/NESTED-HYDRATION.json)

'''
for rel,prefix in [('README.md',readme),('docs/research-plan.md',addition),('docs/AGENT_HANDOFF.md',addition),('docs/results-status.md',addition)]:
 p=root/rel;data=prefix.encode()
 if not p.read_bytes().startswith(data):p.write_bytes(data+p.read_bytes())
 blob=git('hash-object','-w','--stdin',input=data+git('show','HEAD:'+rel)).decode().strip();mode=git('ls-tree','HEAD','--',rel).decode().split(' ',1)[0];subprocess.run(['git','-C',str(root),'update-index','--add','--cacheinfo',mode+','+blob+','+rel],check=True)
with(a/'LOG.md').open('a',encoding='utf-8')as log:log.write('\n'+addition)
scripts=['collect-de8-repeat-final.py','de8-repeat-sealer-tail.py','prepare-repeat-packaging.py','install-repeat-packaging.py','DE8-REPEAT-PACKAGE-TRANSFER.json','start-repeat-official-watch.py','hydrate-repeat-evidence.py','prepare-current-product-normalized-aig.py','value-ir-cache.rs','value-word-aig.rs','prepare-word-value-audit.py','prepare-normalized-anf-word-audit.py','prepare-current-product-anf-audit.py','prepare-public-product-generic-repeat.py','prepare-fast-normalized-anf.py','prepare-fast-normalized-anf-v2.py','prepare-public-semantic-development.py','checkpoint-official-ffe20.py','reference-frame-profile.rs','prepare-reference-frame-profile.py','CURRENT-ACTIVE.json','LOG.md']
paths=['experiments/'+n for n in dirs]+['experiments/autorun-20261020-breakthrough/'+n for n in scripts]+[snap.relative_to(root).as_posix(),'experiments/breakthrough-assessment-20261020/LATEST.json']
subprocess.run(['git','-C',str(root),'add','--',*paths,':!**/public-submissions.json'],check=True)
staged=git('diff','--cached','--name-only').decode().splitlines();allowed=paths+['README.md','docs/research-plan.md','docs/AGENT_HANDOFF.md','docs/results-status.md'];assert all(any(p==q or p.startswith(q+'/')for q in allowed)for p in staged)
assert not any(any('/'+x+'/'in p for x in excluded)or p.endswith('.ops.bin')or p.endswith('.cnf')or p.endswith('.drat')or p.endswith('.jsonl')or p.endswith('/final-evidence.tar.gz')for p in staged)
subprocess.run(['git','-C',str(root),'commit','-q','-m','Preserve official T746112 result and current-parent packed value proofs'],check=True);print(git('rev-parse','HEAD').decode().strip())
