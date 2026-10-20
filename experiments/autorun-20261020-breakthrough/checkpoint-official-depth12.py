import gzip,hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
root=Path(__file__).resolve().parents[2];a=Path(__file__).parent;ex=root/'experiments'
def git(*args,input=None):return subprocess.check_output(['git','-C',str(root),*args],input=input)
assert not git('diff','--cached','--name-only').strip()
final=ex/'breakthrough-depth12-final-20261020';record=json.loads((final/'OFFICIAL-RESULT.json').read_text());assert(record['Q'],record['T'])==(1464,747218)
readme='''## Official Toffoli improvement · 21 October 2026, 03:27 SGT

The challenge officially reproduced **1,464 qubits × 747,218 rounded mean
executed Toffolis = 1,093,927,152**, with all 9,024 shots passing, in
[submission 2bd0f979](https://api.ecdsa.fail/api/submissions/2bd0f979-ab55-4f91-8133-68a08febaa67).
This saves **8 Toffolis at unchanged width**. The fresh 19:27 UTC public records
confirm the independent Toffoli minimum. Global product **933,231,010** remains
lower; promotion was declined because that product did not improve.
Attribution: **GPT-6 sol / Codex**.

The depth-12 exact inverse leaf and 230 existing-wire caches have their own
passed statistical gate, disclosed nonce 41/64 screens, and unchanged benchmark.
All 205 published source files and 17 protected files match the validated source.

[Source and disclosures](experiments/breakthrough-depth12-final-20261020/SUBMISSION-NOTE.md) ·
[Local evidence verification](experiments/breakthrough-depth12-final-20261020/LOCAL-VERIFICATION.json) ·
[Official source verification](experiments/breakthrough-depth12-final-20261020/PUBLIC-SOURCE-VERIFICATION.json)

'''
addition='''## 21 October 2026, 03:27 SGT: official T747218; product gate passes

Auto-submission2bd0f979 officially reproduces Q1464/T747218/product1093927152,
8 fewer Toffolis at unchangedQ. Publicsource36e37af0, localf9cd2058; all205source
and17protected Git-object bytes match. All380evidence/205source members verified
locally; immutablearchive7b91243a, sourcearchive43484f5f. Fresh19:27UTC1713records
confirms independentT minimum, product933231010/acd0 andwidth670/e2 unchanged.
Globalproduct objective remains ACTIVE. Auto-submit each complete verified new
current-record improvement asGPT-6sol/Codex. No default-branch push authorization.

Fixed resource grid before freshinputs: depth12 chosen by actual resource means;
depth16 had no further measured benefit, square1536/walk1664 exactoldstream.
Grouped-depth8 strengthened prototype is control, not unchanged71constructor.
Production exactdepth12/full259correction/witness28; no reduced correctness cut.
Native34/fullsquarecaller/fault controls, then230fresh existing-wire cache leases,
9proofcontrols, fullinput/newoutputcanonical bindings, literalnonce0,205source.
Finalgate depth12-context-final-20261020-v1,32768x64/source PASS against exact71:
wrongvalues1135/1135 identicalIDs,dirty0,failed1170/1172,b9/c7,p.4018096924,
5.04309082failedbatches/packet,pairedT-4.08189249,SE.2986605. Verdict final.
Lowestnonce41,64ascending screens1..64,solepass41,overrun42..64;8extra partial
controls1..8 repeat production,24protectedfullstate/RNG/curve batches,selected
9024replay andunchanged9024benchmarkPASS,total6742892429. Stream63370be6.
Officialstatus rejected solely because globalproduct islower, independentT
metrics reproduced. Development inheritedscope prose oldnumericT isdisclosed;
actualparent71/hash andfinal source/gate are authoritative. No archive rewrite.

Product candidate Q1233 now has its OWN final statistical PASS, not a score:
public-best-drop-product-final-20261020-v1,131072x64=8388608shots/source,declared
19:00:35.220516UTC against exact publicacd0/3d7c94f1. Values14105/14105 sameIDs,
dirty0,failed16438/16484,b1612/c1566,p.2123667109,17.73257446/packet<=18.
MeanTdiagnostic756850.1572 vsparent756259.1151; extraT permitted foronefewerQ.
Gate remains final: never relabel/rerun/extend. SFb2a01786/stream61927788,177source/
17protected. Exact static r012=[0,1,2] resource profile selected before freshpoint
inputs;9proofcontrols/113leases. Checked historicalnonce1052246623534 removed,
literal0 appended; central PROTOTYPE-TAIL-CORRECTION.md remains authoritative.

Initial nonce launcher requested32workers; exactengine rejects above16 BEFORE
qualification or anyscreen. Originalfailure preserved,zero completedscreens.
V2PID3045633/engine3046104,16workers,ascending1..65536/64windows;8partialcontrols
and24protectedfullstate/RNG/curve batches PASS. Over22000exact screens, noPASS
atcheckpoint. LowestcompletePASS only, no resourcebasednonce selection. Ifprefix
exhausts continue ascending with originalsource/gate and disclose everyprefix.
Only afterfullpacketPASS may unchanged benchmark determine a product result;
then localarchive/sourceverification, freshpublicrecords, automaticupload.

Verification-only valueIR native7 PASS; guarded-write dominance/capturedSSA/
value liveness/cancellation reduces dependencies but still10110live RNG defs
onproduct,2465onT71 after32rounds. These are NOT quantum resource counts, no
nonce screened/rejected withIR. Extended auditv2PID3067406 native8 PASS adds
read/writecommutation and2048round bound; currentfullaudit running. Any future
filter must separately qualify exactprotected finalpointvalues andoriginalFS;
fullstate/phase/dirty replay andunchanged benchmark remain mandatory.

Cycle9sixfronts266 andcycle10sevenfronts217 members independentlyverifiedlocally.
Depth12 nestedgrid/proof/dev/gate/search evidence hydrated through immutable
manifestchecks. Preserve alloriginalfailures, protectedharness anduser edits.
Serverchemistry/unrelatedQOBjobs untouched; serverresource inventory notexported.
Automaticapprovalreview rejected sharedmainpush pendingexplicituserapproval;
do not bypass/retry. Localcommits andauthorizedchallengeuploads continue.

'''
for path,prefix in [('README.md',readme),('docs/research-plan.md',addition),('docs/AGENT_HANDOFF.md',addition)]:
 p=root/path;data=prefix.encode();assert not p.read_bytes().startswith(data);p.write_bytes(data+p.read_bytes());base=git('show','HEAD:'+path);blob=git('hash-object','-w','--stdin',input=data+base).decode().strip();mode=git('ls-tree','HEAD','--',path).decode().split(' ',1)[0];subprocess.run(['git','-C',str(root),'update-index','--add','--cacheinfo',mode+','+blob+','+path],check=True)
state=json.loads((a/'CURRENT-ACTIVE.json').read_text());state.update(at_utc=datetime.now(timezone.utc).isoformat(),official_latest=record,local_evidence=json.loads((final/'LOCAL-VERIFICATION.json').read_text()),latest_public_snapshot='experiments/breakthrough-assessment-20261020/snapshots/20261020T192716Z',product_final_gate=json.loads((ex/'breakthrough-public-best-drop-final-gate-20261020/GATE-RESULT.json').read_text()),depth12_final_gate=json.loads((ex/'breakthrough-depth12-final-gate-20261020/GATE-RESULT.json').read_text()),active_jobs=[{'directory':'breakthrough-public-best-drop-nonce-v2-20261020','pid':3045633,'engine_pid':3046104,'purpose':'Qualified exact ascending1..65536/16workers/lowestPASS. Product finalgatePASS; no passingnonce yet atcheckpoint.'},{'directory':'breakthrough-value-ir-audit-v2-20261020','pid':3067406,'purpose':'Verification-only read/writecommuting valueIR;8nativePASS,2048round bound. No nonce filter or quantum candidate.'}],active_submission=None,next_product_front='Finish qualified product nonce search; continue exact ascending prefixes if exhausted. Never costselect a PASS. Then unchanged9024benchmark/full localarchive/source verification/freshrecords andauto-submit any complete product improvement. Separately inspect extended valueIR for sound acceleration; no unqualified rejection shortcut.',new_official_summary='Official2bd0f979 Q1464/T747218 independentT minimum. Globalproduct933231010 remains lower; objective ACTIVE.')
names=['breakthrough-public-drop-tradeoffs-v2-20261020','breakthrough-public-best-drop-context-20261020','breakthrough-public-best-drop-finished-20261020','breakthrough-public-best-drop-development-20261020','breakthrough-public-best-drop-final-gate-20261020','breakthrough-public-best-drop-nonce-20261020','breakthrough-value-ir-audit-20261020']
state['cycle10_verified_completed_evidence']={n:json.loads((ex/n/'LOCAL-VERIFICATION.json').read_text())['members']for n in names};assert sum(state['cycle10_verified_completed_evidence'].values())==217
(a/'CURRENT-ACTIVE.json').write_text(json.dumps(state,indent=2)+'\n')
# Track compact exact copies of large census rows; retain original files/archives.
for name in ['breakthrough-public-best-drop-final-gate-20261020']:
 for filename in ['parent.jsonl','candidate.jsonl']:
  p=ex/name/filename;data=p.read_bytes();gz=gzip.compress(data,mtime=0);assert gzip.decompress(gz)==data;(p.parent/(filename+'.gz')).write_bytes(gz)
dirs=['breakthrough-depth12-'+x+'-20261020'for x in ['context','development','final','final-gate','finished','nonce']]+names+['breakthrough-grouped-exact-resource-grid-v2-20261020','breakthrough-grouped-resource-development-20261020','breakthrough-public-best-drop-nonce-v2-20261020','breakthrough-value-ir-audit-v2-20261020']
scripts=['checkpoint-official-depth12.py','CURRENT-ACTIVE.json','preserve-depth12-and-cycle10.py','seal-research-cycle10.py','collect-research-cycle10.py','collect-depth12-final.py','prepare-depth12-collector.py','prepare-depth12-context.py','prepare-depth12-final-controllers.py','prepare-depth12-finished.py','prepare-depth12-official-checks.py','prepare-depth12-packaging.py','prepare-depth12-verification.py','prepare-public-best-drop-nonce-v2.py','prepare-public-best-drop-nonce.py','prepare-value-ir-audit.py','value-ir-audit.rs','prepare-value-ir-v2.py']
paths=['experiments/'+n for n in dirs]+['experiments/autorun-20261020-breakthrough/'+n for n in scripts]+['experiments/breakthrough-assessment-20261020/snapshots/20261020T192716Z']
subprocess.run(['git','-C',str(root),'add','--',*paths,':!**/parent.jsonl',':!**/candidate.jsonl',':!**/public-submissions.json'],check=True)
allowed=paths+['README.md','docs/research-plan.md','docs/AGENT_HANDOFF.md'];staged=git('diff','--cached','--name-only').decode().splitlines();assert all(any(p==q or p.startswith(q+'/')for q in allowed)for p in staged);assert not any('resource-preflight'in p or'/candidate/'in p or'/observer/'in p or'/tool/'in p or p.endswith('ops.bin')for p in staged)
subprocess.run(['git','-C',str(root),'commit','-q','-m','Preserve official T747218 improvement and qualified product gate PASS; continue exact search'],check=True);print(git('rev-parse','HEAD').decode().strip())
