import hashlib,json,subprocess
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[2];a=Path(__file__).parent;ex=root/'experiments';sha=lambda b:hashlib.sha256(b).hexdigest()
def git(*args,input=None):return subprocess.check_output(['git','-C',str(root),*args],input=input)
assert not git('diff','--cached','--name-only').strip()
completed=['breakthrough-value-failure-fixture-audit-20261020','breakthrough-value-affine-audit-20261020','breakthrough-value-affine-audit-v2-20261020']
results={}
for name in completed:
 r=ex/name;assert(r/'run.exit').read_text().strip()=='0';f=json.loads((r/'SOURCE-FREEZE.json').read_bytes());assert all(sha((r/'local-tool'/p).read_bytes())==h for p,h in f['source_files'].items());j=json.loads((r/'full-audit.json').read_bytes());curve=j['curve_audit'];results[name]={'status':'COMPLETED_VERIFICATION_ONLY_NO_NONCE_REJECTED','native_controls':f['native_controls'],'known_output_bits':[b['known_output_bits']for b in curve['batches']],'certified_wrong_shots':[b['certified_wrong_shots']for b in curve['batches']],'concrete_wrong_shots':[[p['wrong_shots']for p in b['concrete_patterns']]for b in curve['batches']],'protected_fullstream_value_comparisons':30,'budget_events':[s for s in(r/'full-audit.log').read_text().splitlines()if s.startswith('AFFINE_BUDGET_EXHAUSTED')],'scope':f['scope']};(r/'LOCAL-RESULT.json').write_text(json.dumps(results[name],indent=2)+'\n')
 files={p.relative_to(r).as_posix():sha(p.read_bytes())for p in r.rglob('*')if p.is_file()and'local-tool'not in p.relative_to(r).parts and p.name!='LOCAL-EVIDENCE-MANIFEST.json'};(r/'LOCAL-EVIDENCE-MANIFEST.json').write_text(json.dumps({'files':files,'source_files_reverified':f['source_files'],'scope':'Every saved local evidence file hashed; separate verification tools/fixtures, not quantum submissions.'},indent=2)+'\n')
state=json.loads((a/'CURRENT-ACTIVE.json').read_bytes());state.update(at_utc=datetime.now(timezone.utc).isoformat(),server_access='SSH timed out repeatedly after21:06UTC; last remote Boolean-reset job PID3143340 native17PASS and running. Final status unknown; do not assume stopped. Pending remote product transfer/launch unconfirmed.',active_jobs=[{'environment':'WSL Ubuntu local','pid':444,'directory':'breakthrough-local-product-filter-replay-20261020','purpose':'Exact old product stream61927788 reproduced locally,177source/17protected unchanged. Native20 guard-fusion whole-stream audit running.'},{'environment':'WSL Ubuntu local','pid':1332,'directory':'breakthrough-public1829-width-port-local-v2-20261020','purpose':'Native9PASS and exactpublic1829 stream16567ee1 reproduced. cap1234/cap1233 exact workspace resource variants generating; old boundtables deliberately omitted in changed branches.'},{'environment':'WSL Ubuntu local','pid':4712,'directory':'breakthrough-value-curve-audit-v2-20261020','purpose':'Native21PASS; fixed32validcurve fixtures with96protected comparisons after full exact IR optimization.'},{'environment':'remote last known','pid':3143340,'directory':'breakthrough-value-boolean-reset-audit-20261020','purpose':'Native17PASS; status unknown until SSH recovered.'}],local_completed_verifier_research=results,next_product_front='Finish declared local public1829 exact workspace resource grid. Reprove fresh caches if competitive; fresh actual-resource development and OWN final gate vs exact public1829 before any nonce/benchmark/upload. In parallel improve exact wrongpoint certificates; prior non-curve unknown results do not establish valid-curve failure-filter impossibility.',local_source_reproduction=json.loads((ex/'breakthrough-local-product-filter-replay-20261020/STREAM-REPRODUCTION.json').read_bytes()))
(a/'CURRENT-ACTIVE.json').write_text(json.dumps(state,indent=2)+'\n')
prefix='''## 21 October 2026: local research continues through server outage

Official de8bac6a Q1464/T746114 remains the latest verified result in our
21:03UTC public snapshot. No new score or nonce search since that submission.
SSH to smu_server timed out repeatedly after21:06UTC; remote Boolean-reset job
3143340 was last native17PASS/running. Its final status is unknown; no jobs killed.
Pending remote workspace transfer/launch unconfirmed. Chemistry untouched.

Existing local WSL compiler1.99 used in separate research folders. All17protected
dependencies restored to EXACT server-frozen LF bytes; no harness edits. Old
Q1233 source177files reproduces exactstream61927788 under localcompiler; remains
superseded, no old gate/nonce/benchmark/upload resumed. Its new guard-fusion
verification-only audit native20PASS/fullstatic audit running. Public1829 source
186files also reproduces exactpublishedstream16567ee1 under the local resource
grid. Native9comparator/plan/policy controlsPASS. Three predeclared modes public,
cap1234-t21, cap1233-r012; only exact workspace changes, public approximations
unchanged. Changed branches OMIT old boundtables, retain generic passes; no
hash binding disabled/repointed. Fresh cache proofs required if competitive.

Two local setup failures retained: first workspace adapter stopped before
source changes/tests on whitespace-sensitive dependency path replacement;
curve-fixture tool stopped before input tests because U256 lacks u64 Into.
Corrected separatev2 folders retain originals. Native shell first failed onCRLF
beforecompile; LF launcher fixes it. Offline cache miss preserved; locked
dependencies fetched for separate verification tools. No failure called a pass.

Filter fixtures: earlier arbitrary registered bit patterns do NOT establish
anything about valid-curve usefulness. New curve tool native21PASS tests32fresh
validcurve batches/96protected value comparisons, fullstatic audit stillrunning.
Separately first128 preserved oldvalue-failure scalars, rawexact captured-SSA IR:
native21/30protected value comparisons PASS; all128 wrong under all3RNGpatterns,
but zero certifiedknown/wrong bits. No nonce screened/rejected or gate rerun.

Bounded Boolean ANF retains exact XOR/AND/ITE correlations, opaque atoms widen
possibilities, structural equality only; truth samples NEVER select certificates.
Native23PASS/30protected comparisons on same128 verifier fixtures. Original2m
and separate8m monomial budgets both exhaust, returning ALLUNKNOWN, zero certified
wrong bits. Negative/budget-limited results preserved with full frozen tool source,
fixtures, logs and hashes. These are verification-only counts, NOT quantum
resources. Further exact filter research and complete product objective active.

Every verified current-record improvement still goes automatically to challenge
verification as GPT-6 sol/Codex. Default-branch push remains blocked by automatic
approval review pending explicit approval; no retry/bypass. User edits preserved.

'''
for path in ['docs/research-plan.md','docs/AGENT_HANDOFF.md']:
 p=root/path;data=prefix.encode();p.write_bytes(data+p.read_bytes());blob=git('hash-object','-w','--stdin',input=data+git('show','HEAD:'+path)).decode().strip();mode=git('ls-tree','HEAD','--',path).decode().split(' ',1)[0];subprocess.run(['git','-C',str(root),'update-index','--add','--cacheinfo',mode+','+blob+','+path],check=True)
dirs=completed+['breakthrough-value-guard-fusion-audit-20261020','breakthrough-local-product-filter-replay-20261020','breakthrough-public1829-width-port-local-20261020','breakthrough-public1829-width-port-local-v2-20261020','breakthrough-value-curve-audit-20261020','breakthrough-value-curve-audit-v2-20261020']
scripts=['CURRENT-ACTIVE.json','checkpoint-local-filter-research.py','prepare-value-guard-fusion-audit.py','prepare-local-filter-tests.py','prepare-local-product-replay.py','prepare-local-public1829-port.py','prepare-local-public1829-port-v2.py','prepare-value-curve-audit.py','prepare-value-curve-audit-v2.py','prepare-value-failure-fixture-audit.py','value-affine-audit.rs','value-affine-audit-v2.rs','prepare-value-affine-audit.py','prepare-value-affine-audit-v2.py','audit-public1829-static-tables.py']
paths=['experiments/'+d for d in dirs]+['experiments/autorun-20261020-breakthrough/'+n for n in scripts]+['experiments/breakthrough-public1829-reproduction-20261020/'+n for n in ['constructor-reference.rs','source-edits-reference.rs','stream-edits-reference.rs']]
subprocess.run(['git','-C',str(root),'add','--',*paths],check=True);staged=git('diff','--cached','--name-only').decode().splitlines();assert all(any(p==q or p.startswith(q+'/')for q in paths+['docs/research-plan.md','docs/AGENT_HANDOFF.md'])for p in staged);assert not any('/candidate/'in p or'/observer/'in p or'/local-tool/'in p or'/local-protected/'in p or'preflight'in p or p.endswith('ops.bin')for p in staged)
subprocess.run(['git','-C',str(root),'commit','-q','-m','Preserve exact local source reproductions and bounded failure-filter audits'],check=True);print(git('rev-parse','HEAD').decode().strip())
