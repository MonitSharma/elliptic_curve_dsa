"""Preserve only owned changes; keep pre-existing user doc edits unstaged."""
import gzip,hashlib,json,subprocess
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[2];a=Path(__file__).parent;ex=root/'experiments'
def git(*args,input=None):return subprocess.check_output(['git','-C',str(root),*args],input=input)
sha=lambda b:hashlib.sha256(b).hexdigest()
assert not git('diff','--cached','--name-only').strip()
r=ex/'breakthrough-exact-witness-final-20261020';official=json.loads((r/'OFFICIAL-RESULT.json').read_bytes());assert official['T']==746114
local=json.loads((r/'LOCAL-VERIFICATION.json').read_bytes());assert local['members']==329
assert json.loads((r/'PUBLIC-SOURCE-VERIFICATION.json').read_bytes())['source_files']==205
assessment=ex/'breakthrough-assessment-20261020';snap=assessment/json.loads((assessment/'LATEST.json').read_bytes())['snapshot'];records=json.loads((snap/'PUBLIC-RECORDS.json').read_bytes());assert records['leaders']['toffoli']['id']==official['submission']
raw=(snap/'public-submissions.json').read_bytes();(snap/'public-submissions.json.gz').write_bytes(gzip.compress(raw,mtime=0));files=['leader-product.json','leader-qubits.json','leader-toffoli.json','PUBLIC-RECORDS.json','public-submissions.json.gz'];(snap/'SNAPSHOT-MANIFEST.json').write_text(json.dumps({'raw_api_sha256':sha(raw),'files':{n:sha((snap/n).read_bytes())for n in files},'scope':'Fresh official public records; independent T minimum de8bac6a, product1829, width669/1df8.'},indent=2)+'\n');(snap/'.gitattributes').write_text('* -text\n')
state=json.loads((a/'CURRENT-ACTIVE.json').read_bytes());state.update(at_utc=datetime.now(timezone.utc).isoformat(),official_latest=official,local_evidence={**local,'scope':'All immutable pre-upload evidence/source verified locally; subsequent official evaluation and complete published source bytes separately verified.'},latest_public_snapshot=snap.relative_to(root).as_posix(),public_product=records['leaders']['product'],public_width=records['leaders']['qubits'],active_jobs=[{'directory':'breakthrough-value-boolean-reset-audit-20261020','pid':3143340,'purpose':'Native17 PASS; verification-only source-bound Boolean reset implication audit. No nonce rejection or quantum resource claim.'}],active_submission=None,new_official_summary='Official de8bac6a Q1464/T746114, 1104 fewer T at unchanged width; officially reproduced, promotion declined solely lower global product. GPT-6 sol/Codex. Global product goal ACTIVE.',next_product_front='Exact workspace port prepared on new public1829. Three fixed modes public/cap1234-t21/cap1233-r012, old static edit tables omitted entirely only in research variants; fresh proofs required. Transfer timed out, launch unconfirmed; check before retry. Verification-only exact failure-filter research continues.',old_product_search_terminal=json.loads((ex/'breakthrough-public-best-drop-nonce-v2-20261020/SEARCH-RESULT.json').read_bytes()),exact_witness_pipeline='All grid/development/proof/finished/finalgate/nonce/finalbenchmark/upload/source checks DONE; 329-member immutable archive locally verified; 248 nested files hydrated with every hash checked. Never duplicate upload.',value_dominance_negative='Native15, 24 protected whole-stream value comparisons; fixedpoint reached but zero known output bits on all8 fixtures. No nonce rejection; completed server evidence awaits collection.')
(a/'CURRENT-ACTIVE.json').write_text(json.dumps(state,indent=2)+'\n')
readme='''## Official Toffoli improvement · 21 October 2026, 05:03 SGT

The challenge officially reproduced **1,464 qubits × 746,114 rounded mean
executed Toffolis = 1,092,310,896** in
[submission de8bac6a](https://api.ecdsa.fail/api/submissions/de8bac6a-afff-479e-b716-8cbf2dce6c73).
This saves **1,104 Toffolis at unchanged width**. All 9,024 benchmark shots
pass, and all 205 published source files and 17 protected files match the
validated local source. Attribution: **GPT-6 sol / Codex**.

The fresh 21:03 UTC public snapshot confirms the independent Toffoli minimum.
The product record remains **932,057,476** (Q1234/T755314); promotion was
declined solely because that product is lower. The global product objective
remains active. The public width minimum is now 669 qubits.

[Source and disclosures](experiments/breakthrough-exact-witness-final-20261020/SUBMISSION-NOTE.md) ·
[Official source verification](experiments/breakthrough-exact-witness-final-20261020/PUBLIC-SOURCE-VERIFICATION.json) ·
[Evidence verification](experiments/breakthrough-exact-witness-final-20261020/NESTED-HYDRATION.json)

'''
addition='''## 21 October 2026, 05:03 SGT: official T746114; exact product research continues

Official submission de8bac6a-afff-479e-b716-8cbf2dce6c73 reproduces Q1464,
T746114, product1092310896: 1104 fewer T at unchanged width. Public source
bd6672a873f85953eb7c5197e9cf46982ce19708; local feba56deec6e98e58901e06358841d246e63ad10.
All205 source/17protected Git-object bytes match;329 immutable evidence members
and205source files locally verified;248nested files hydrated with all hashes.
Official rejected solely because global product is lower. GPT-6 sol/Codex.
Fresh21:03UTC1716records confirms Tminimum; product1829 Q1234/T755314/932057476;
newwidth669/1df8/source4c1c3140. Global product goal remains ACTIVE.

New exact full259 witness polynomial consolidates five full-width translations;
no public59-bit truncation imported. Exact copied sharedsum and depth12 leaf,
28bit wrap witness, full group/correction tails and prior windows remain.
Five resource cases frozen before inputs; combined selected by actual meanT.
V1 setup and V2 cached fault-switch failures preserved separately; V3 native
controls pass with direct environment reads and fault-then-clean regression.
Fresh230 existing-wire caches with9proof controls; finishedsource205files/native7.

Sole final gate full259-witness-final-20261020-v1,32768x64/source, exactpublic2bd:
value failures1131/1131 identicalIDs, dirty0, failed batches1169/1163, b8/c14,
p=.9330997467041016, candidate5.004364013671875failed batches/packet. PASS final;
never rerun/relabel/extend. Qualified ascending1..256 nonce search, lowestPASS229,
onlyPASS229, overrun230..256;8extra partialnonce/24protected fullstate controls.
Selected9024replay and unchanged9024benchmark PASS,totalT6732932893,
mean746114.0173980496, rounded746114. Finalstream131712cc9c79e9ffd3ac60c07d097a29b5252c03afa95c891c5ecdd603c60c2e.
Archive9735d309d166746eec10ff58de5318c0d1d37d750e50e6b2378530baa8226aca.
One upload only, officialsource checkDONE; do not resubmit same result.

Old superseded Q1233/acd0 finite search exhausted1..65536 withoutPASS. Its old
gatePASS remains final; no continuation/benchmark/upload. All19evidence members
verified locally; negative rows retained compressed. No reinterpretation.

Verification-only dominance audit native15 and24full protected value comparisons
PASS but all8fixtures have zero certified knownoutput bits; no useful filter.
Boolean reset audit native17PASS, PID3143340: conservative possible-write Boolean
conditions, soundstructural or bounded exhaustive <=10atom implication, no sampled
identities. No quantum candidate/phase claim or nonce rejection. Source-bound
filter may only reject a nonce using an EXACT wrongpoint witness. Prior negative
audits retained; IR counts never scored. Product port prepared on new1829 parent:
exact public bytecontrol, uncached cap1234 and exactcarry cap1233/r012; original
boundtables preserved and OMITTED only in explicit research branches, never
repointed. Own fresh proofs/gate/nonce/unchangedbenchmark required for submission.
Transfer timedout; confirm serverdirectory/launch before retry.

Automatic challenge submissions remain authorized for every complete verified
current-record improvement. Default-branch push remains blocked by automatic
approval review pending explicit user approval; do not retry or bypass it.
Pre-existing user changes and unrelated server jobs/chemistry remain untouched.

'''
for path,prefix in [('README.md',readme),('docs/research-plan.md',addition),('docs/AGENT_HANDOFF.md',addition),('docs/results-status.md',addition)]:
 p=root/path;data=prefix.encode();assert not p.read_bytes().startswith(data);p.write_bytes(data+p.read_bytes());blob=git('hash-object','-w','--stdin',input=data+git('show','HEAD:'+path)).decode().strip();mode=git('ls-tree','HEAD','--',path).decode().split(' ',1)[0];subprocess.run(['git','-C',str(root),'update-index','--add','--cacheinfo',mode+','+blob+','+path],check=True)
dirs=['breakthrough-exact-witness-context-20261020','breakthrough-exact-witness-final-20261020','breakthrough-exact-witness-final-gate-20261020','breakthrough-exact-witness-finished-20261020','breakthrough-exact-witness-finished-development-20261020','breakthrough-exact-witness-nonce-20261020','breakthrough-exact-witness-ripple-v3-20261020','breakthrough-exact-witness-development-20261020','breakthrough-public-best-drop-nonce-v2-20261020','breakthrough-value-dominance-audit-20261020','breakthrough-value-boolean-reset-audit-20261020','breakthrough-public1829-width-port-20261020']
for name in dirs:
 d=ex/name
 for p in d.glob('*.jsonl'):
  if p.stat().st_size>1000000:(p.with_suffix(p.suffix+'.gz')).write_bytes(gzip.compress(p.read_bytes(),mtime=0))
 p=d/'.gitignore';s=p.read_text()if p.exists()else''
 for n in ['*.jsonl','evidence.tar.gz','final-evidence.tar.gz','*resource-preflight*','tool-source/target/']:
  if n not in s.splitlines():s+=n+'\n'
 p.write_text(s)
scripts=['CURRENT-ACTIVE.json','checkpoint-official-witness.py','hydrate-exact-witness-evidence.py','prepare-value-dominance-audit.py','prepare-value-boolean-reset-audit.py','prepare-public1829-width-port.py','prepare-exact-witness-context.py','prepare-exact-witness-finished.py','prepare-exact-witness-verification.py','prepare-exact-witness-final-controllers.py','prepare-exact-witness-packaging.py','exact-witness-sealer-tail.py','prepare-exact-witness-local-watch.py','collect-exact-witness-final.py','watch-exact-witness-local.py','prepare-cycle13-collection.py','seal-research-cycle13.py','collect-research-cycle13.py']
paths=['experiments/'+n for n in dirs]+['experiments/autorun-20261020-breakthrough/'+n for n in scripts]+[snap.relative_to(root).as_posix()]
subprocess.run(['git','-C',str(root),'add','--',*paths,':!**/public-submissions.json'],check=True)
staged=git('diff','--cached','--name-only').decode().splitlines();allowed=paths+['README.md','docs/research-plan.md','docs/AGENT_HANDOFF.md','docs/results-status.md'];assert all(any(p==q or p.startswith(q+'/')for q in allowed)for p in staged)
assert not any('resource-preflight'in p or'/candidate/'in p or'/observer/'in p or'/tool/'in p or p.endswith('ops.bin')for p in staged)
subprocess.run(['git','-C',str(root),'commit','-q','-m','Preserve officially verified T746114 improvement and fresh product research'],check=True);print(git('rev-parse','HEAD').decode().strip())
