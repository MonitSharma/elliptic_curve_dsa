import json,subprocess
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[2];a=Path(__file__).parent
def git(*args,input=None):return subprocess.check_output(['git','-C',str(root),*args],input=input)
assert not git('diff','--cached','--name-only').strip()
record=json.loads((root/'experiments/breakthrough-groups-safe-final-20261020/OFFICIAL-RESULT.json').read_text());assert record['T']==747453
state=json.loads((a/'CURRENT-ACTIVE.json').read_text());state.update(at_utc=datetime.now(timezone.utc).isoformat(),official_latest=record,local_evidence=json.loads((root/'experiments/breakthrough-groups-safe-final-20261020/LOCAL-VERIFICATION.json').read_text()),latest_public_snapshot='experiments/breakthrough-assessment-20261020/snapshots/20261020T163228Z',active_jobs=[{'directory':'breakthrough-grouped-compact-width-v2-20261020','pid':2948021,'purpose':'Native4 PASS, prior27/group/squareunits PASS; fullcontrol then lowercaps1234/1233 generation. New exact one-carry terminal phase expansion, totaldrawcount preserved. Not scored.'},{'directory':'breakthrough-groups-safe-context0-20261020','pid':2953122,'purpose':'Fixed exact context16384/arbitraryzero proof on official8d streamccdef4d6;9nativecontrols before component; no addedQ.'},{'directory':'breakthrough-groups-safe-context16-20261020','pid':2953178,'purpose':'Same exact proof/native controls on official8d,16additional donors <=Q1480 for independentT; no gate/score yet.'}],push_status='Commit41f769ec remains local. Auto-review rejected default-branch push; explicit user approval requested asynchronously, no bypass/retry.',cycle3_verified_completed_evidence={n:json.loads((root/'experiments'/n/'LOCAL-VERIFICATION.json').read_text())['members']for n in ['breakthrough-live-products-absorption-v2-20261020','breakthrough-public-e3-live-finished-20261020','breakthrough-public-e3-live-development-20261020','breakthrough-public-e3-live-final-gate-20261020','breakthrough-native-context-finished-20261020','breakthrough-native-context-finished-v2-20261020','breakthrough-grouped-square-caps-20261020','breakthrough-grouped-compact-width-20261020']})
(a/'CURRENT-ACTIVE.json').write_text(json.dumps(state,indent=2)+'\n')
addition='''## 21 October 2026, 00:35 SGT: official Q1464/T747453; product goal active

New auto-submission8d0fef2b officially reproduces Q1464/T747453/product1094271192,
731 fewerT and16 fewerQ vs preceding38a686dd. Publicsourced289ee2b; all204source
and17protected bytes verified against Git objects; localab071cf3. All324evidence
and204source members independently verified. Officialpromotion rejected solely
because globalproduct is lower. Fresh16:32UTC1710records confirms independentT
minimum, globalproduct933231010/acd0 andwidth670/e2 unchanged. Never claimglobal
product victory. Userauthorizes automatically submitting each verified improvement.

Own grouped-safe finalgate PASS32768x64/source, labelgroups-safe28-full259-final-
20261020-v1. Value1227parent/1216candidate,6newbad/17newpass,dirty0,failed1273/1255,
b15/c33,p.997242399,5.400238failedbatches/packet; no rerun/relabel/extension.
Qualifiedlowestnonce282 of320ascendingproduction screens (solepass282), overrun
283..320,8extra partialcontrols1..8 repeated/24protectedfullstate batches,
selected9024 replay PASS. Unchangedbenchmark9024 PASS,total6745013540,exactmean
747452.7415780142. Streamccdef4d6,records b3884311,pretail e7b65a3d;finalarchive
9fed794b,sourcearchive6a657aec,patcha453eb39. Sourceonlynonceconstant differs
from gatednonce0dc1478. Strong28bit/full259tail/exactsplits/depth8 square/native
rail/G6; six historical squareunit edge exclusions disclosed, no universal claim.

Activewidth probe2948021: originalv1 equaldraw assertion failed before semantic
comparisons; broadfaultshouldpanic falsely accepted samefixturefailure. Preserved.
V2 twozeroHMRs replace omittedR+HMR; fault expects specificphasecontract. Native4
PASS incl exhaustivebasis/phase/wide/guards/aliasseeds/RNG/width; inherited27 and
squareunits pass. Fullcontrol/lowcap1234/1233 construction now running; measuredQ
must be read, cap is not Q. New exact comparator expands final nestedMAJ and
savesonecarry with+1nativeT onlywhenoldrouteexceeds cap. y16 cost formula reflects
proved newhelpercount; original primitive/admission/precision guards preserved.

Two independent exactcontext scans on official8d:2953122 zeroaddedQ and2953178
16donors<=1480; exact arbitrarycut donorzero proof, fixed16384 same lexicalscope,
9native controls before scans. Componentonly; any finishedcandidate needs fresh
own finalgate versus exact currentrecord, qualifiednonce, unchangedbenchmark and
localmember verification. Read CURRENT-ACTIVE.json and actual job logs.

Eight completedresearchfronts275 members verified locally, including partial
assemblysource archives/patches and e3 preflight supersededbeforedeclaration.
Immutable finalarchives remain authoritative; nested evidence hydrated with
manifest checks andlinks. Mainpush41f769ec blocked byautomaticapprovalreview;
explicitapproval requested, no bypass. Localcommits/research/officialuploads
continue. Preserve all preexistinguserdiffs/submodules andunrelatedserverjobs.

'''
readme='''## Official Toffoli improvement · 21 October 2026, 00:35 SGT

The challenge officially reproduced **1,464 qubits × 747,453 rounded mean
executed Toffolis = 1,094,271,192**, all9,024 shots passing, in
[submission8d0fef2b](https://api.ecdsa.fail/api/submissions/8d0fef2b-a7f6-40a7-9b3c-f800073cf2c5).
This saves **731 Toffolis and16 qubits** versus the preceding official result.
The fresh16:32UTC public records confirm the independent Toffoli minimum.
Global product933,231,010 remains lower; promotion was declined solely because
that score did not improve. Attribution **GPT-6 sol / Codex**.

The grouped square uses28-bit witnesses, full259-bit correction tails and exact
capped splits on our strengthened arithmetic. Its own final statistical gate,
lowestnonce282/320screens and complete unchanged benchmark are disclosed.
Every published source/protected byte matches the locally validated source.

[Source and disclosures](experiments/breakthrough-groups-safe-final-20261020/SUBMISSION-NOTE.md) ·
[Local evidence verification](experiments/breakthrough-groups-safe-final-20261020/LOCAL-VERIFICATION.json) ·
[Official source verification](experiments/breakthrough-groups-safe-final-20261020/PUBLIC-SOURCE-VERIFICATION.json)

'''
for path,prefix in [('README.md',readme),('docs/AGENT_HANDOFF.md',addition),('docs/research-plan.md',addition)]:
 p=root/path;data=prefix.encode();assert not p.read_bytes().startswith(data);p.write_bytes(data+p.read_bytes());base=git('show','HEAD:'+path);blob=git('hash-object','-w','--stdin',input=data+base).decode().strip();mode=git('ls-tree','HEAD','--',path).decode().split(' ',1)[0];subprocess.run(['git','-C',str(root),'update-index','--add','--cacheinfo',mode+','+blob+','+path],check=True)
dirs=['breakthrough-groups-safe-final-20261020','breakthrough-groups-safe-finished-20261020','breakthrough-groups-safe-development-20261020','breakthrough-groups-safe-final-gate-20261020','breakthrough-groups-safe-nonce-20261020','breakthrough-groups-safe-context0-20261020','breakthrough-groups-safe-context16-20261020','breakthrough-native-both-context16-20261020','breakthrough-native-context-finished-20261020','breakthrough-native-context-finished-v2-20261020','breakthrough-native-context-finished-v3-20261020','breakthrough-native-context-development-20261020','breakthrough-native-context-final-gate-20261020','breakthrough-native-context-nonce-20261020','breakthrough-grouped-square-ports-20261020','breakthrough-grouped-square-caps-20261020','breakthrough-grouped-compact-width-20261020','breakthrough-grouped-compact-width-v2-20261020','breakthrough-live-products-absorption-v2-20261020','breakthrough-public-e3-live-finished-20261020','breakthrough-public-e3-live-development-20261020','breakthrough-public-e3-live-final-gate-20261020']
scripts=['checkpoint-official8d.py','phase-compare-compact.rs','prepare-grouped-compact-width.py','prepare-groups-safe-context.py','hydrate-submission-evidence.py','seal-research-cycle3.py','prepare-cycle3-collection.py','collect-research-cycle3.py','prepare-groups-safe-official-checks.py','CURRENT-ACTIVE.json']
paths=['experiments/'+n for n in dirs]+['experiments/autorun-20261020-breakthrough/'+n for n in scripts]+['experiments/breakthrough-assessment-20261020/snapshots/20261020T163228Z']
subprocess.run(['git','-C',str(root),'add','--',*paths],check=True);allowed=paths+['README.md','docs/AGENT_HANDOFF.md','docs/research-plan.md'];staged=git('diff','--cached','--name-only').decode().splitlines();assert all(any(p==q or p.startswith(q+'/')for q in allowed)for p in staged);assert not any('resource-preflight'in p or'/candidate/'in p or'/observer/'in p or'/tool/'in p or p.endswith('ops.bin')for p in staged)
subprocess.run(['git','-C',str(root),'commit','-q','-m','Preserve official Q1464 T747453 and complete evidence; continue exact product research'],check=True);print(git('rev-parse','HEAD').decode().strip())
