import json,subprocess
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[2];a=Path(__file__).parent
def git(*args,input=None):return subprocess.check_output(['git','-C',str(root),*args],input=input)
assert not git('diff','--cached','--name-only').strip();final=root/'experiments/breakthrough-groups-context-final-20261020';record=json.loads((final/'OFFICIAL-RESULT.json').read_text());assert record['T']==747226
state=json.loads((a/'CURRENT-ACTIVE.json').read_text());state.update(at_utc=datetime.now(timezone.utc).isoformat(),official_latest=record,local_evidence=json.loads((final/'LOCAL-VERIFICATION.json').read_text()),latest_public_snapshot='experiments/breakthrough-assessment-20261020/snapshots/20261020T170204Z',active_jobs=[{'directory':'breakthrough-grouped-compact-width-v7-20261020','pid':2969452,'purpose':'Compose native-verified exact measured-prefix/reversible-tail comparator with explicit exactbudget7..9/50bit/drop3 selector and boundedcore equalitycap1234 route. Native4+27/group/square controls, unchangeda871 fullcontrol, completecap1234/1233 construction. No gate/score.'}],active_submission=None,cycle4_verified_completed_evidence={n:json.loads((root/'experiments'/n/'LOCAL-VERIFICATION.json').read_text())['members']for n in ['breakthrough-grouped-compact-width-v2-20261020','breakthrough-grouped-compact-width-v3-20261020','breakthrough-grouped-compact-width-v4-20261020','breakthrough-grouped-compact-width-v5-20261020','breakthrough-grouped-compact-width-v6-20261020']},next_product_front='Read v7 complete construction. If failed, preserve exact guard/budget and derive/test a new legal component or selector. v6 reversible comparator can save n-2 helpers at one extra nativeT per savedhelper; fullnative4includingallcuts/phase/RNG PASS. Do not claim a width result without complete protected analyzer and passing benchmark. Any product candidate needs own finalgate against exact publicacd0 stream, not ourT parent.',new_official_summary='38a686dd T748184,Q1480;8d0fef2b T747453,Q1464;71d9dc7e T747226,Q1464. All auto-submitted/official/source bytes verified. Global product933231010 remains lower and active goalunfinished.')
(a/'CURRENT-ACTIVE.json').write_text(json.dumps(state,indent=2)+'\n')
addition='''## 21 October 2026, 01:02 SGT: official Q1464/T747226; continue product research

New auto-submission71d9dc7e officially reproduces Q1464/T747226/product1093938864,
227 fewerT atunchangedQ vs8d. Publicsource28a4e93e, local3c7e627a; all205source
and17protected Git-object bytes match. All186evidence/205source members verified
locally. Officialpromotion rejected solely because globalproduct islower. Fresh
17:02UTC1711records confirms Tminimum747226; product933231010/acd0/Q1234/T756265
andwidth670/e2 unchanged. Globalproduct goalactive; auto-submit every newcomplete
verified current-record improvement asGPT6sol/Codex. Never declaregoalcomplete.

Bothfixedexactcontext scans (0/16permitteddonors) prove same230leases/output,
actualQ1464/maxdonor1460/noaddedwire,1154nominees/924rejects,9nativecontrols each.
Wholepublic8d constructor preserved; fullparent/input/cacheoutput canonical
bindings,checkedoldnonce282tail removed,nonce0d0e05c59; no genericrepass ornew
precision/window/cut/round. FinishedSF48d46460, native runtime1PASS. Fresh512x64
dev: wrongvalues12sameIDs,dirty0,target/otherdiff0;phase9/5,failed13/12.
Sole groups-context230-final-20261020-v1 gate32768x64/source PASS: value1165/1165
identicalIDs,phase637/637,dirty0,failed1191/1190,b7/c8,p.6963806152,5.120544/packet,
pairedT-228.734732,SE.323315. Declarationc67c713c/result75e97edd. No relabel/rerun.
Qualifiedlowestnonce179,192production screens1..192,solepass179,overrun180..192;
8additionalpartialcontrols1..8 repeat/24protectedfullstatebatches,selected9024
replayPASS. Unchangedbenchmark9024PASS,total6742964592. Finalstream278802f0,
records2a44fb48,pretail392e2e43,sourcearchive1fcd767b,patch377f0aec,finalarchive
c7fbfd62. Sourcechangesonlynonce0->179 fromgatedsource. No globalproductclaim.

Major newcomponent: exact measured-prefix/reversible-tail phasecompare. Keepm
cleanmeasured carries; omittedtail steps use in-place MAJ onoperandwires,
terminalthreeCZphase,reverseMAJundo,thenoriginalprefixHMR. Eachsavedhelpercosts
oneextra nativeT; maxn-2 savedhelpers leavesoneprefixcarry. All2k omittedR/HMR
draws replacedbyzeroHMR. Native4 PASSallsmallbasis/alllegalcuts, wide3..256,
guards/sourcealiasseeds/value/phase/dirty/RNG/peak/fault; fulla871 control exact.
V6 lowcap constructions stillfailfoldguard, no pointstream/score. Earlier
v1drawfixturefail,v2onehelper,v3compilefail,v4quartic,v5dirtylinear-ladder
prototypes all retained; nativepassedwhereapplicable, no scoredresourceclaims.
V3 compilefailure is iteratorfixture, not arithmetic; V6 initialone-linelocal
quotingfailure made nosourcechange/workload, dedicatedhelpercorrects it.

Activev7 PID2969452 composes v6 with independentlynativeverified seven/eight/nine
helper50bit exactfoldplans. Explicitnewcheckedbranch budget7..9/drop>=10-budget;
oldguardremains. Exactdrop3 fwd123..136/rev124..126 onlylowcapmode. Existingcore
route admittedatequalitycap1234 onlywithbothcaps1234/core_room>=30 andallprior
preconditions; originalsmaller-cap route stays. No newapprox/tabletransport.
Native4+27/group/squareunits thenfullcontrola871 andcap1234/1233 generation.
ReadactualmeasuredQ; nominalcap is notQ. Productcandidate needsownexactpublicacd0
gate, notTparent. Ifanotherguardstops, preserve andderive/test nextlegalroute.

Fivecompletedfronts482members independentlyverified andsources/patches retained.
Nestedsubmissionevidence hydratedthroughmanifestchecks/immutablearchivelinks.
Lastpushedroot9ede0ce7; laterlocal41f769ec/fdf747b3 andthischeckpoint awaitpush.
Automaticreview rejected sharedmainpush; explicituserapproval requested,no
bypass/retry. Localwork andauthorizedofficialsubmissionscontinue. Preserve all
preexistinguserroot/submodule edits andunrelatedserverQOBjobs; chemistryuntouched.

'''
readme='''## Official Toffoli improvement · 21 October 2026, 01:02 SGT

The challenge officially reproduced **1,464 qubits × 747,226 rounded mean
executed Toffolis = 1,093,938,864**, all9,024 shots passing, in
[submission71d9dc7e](https://api.ecdsa.fail/api/submissions/71d9dc7e-550b-480d-8d9e-c2af1989c0d7).
This saves **227 Toffolis at unchanged width** versus the preceding official
result. The fresh17:02UTC records confirm the independent Toffoli minimum.
Global product933,231,010 remains lower; promotion was declined solely because
that score did not improve. Attribution **GPT-6 sol / Codex**.

The230 exact contextual caches use existing wires. Their own final statistical
gate, lowestnonce179/192screens and complete unchanged benchmark are disclosed.
Every published source/protected byte matches the validated local source.

[Source and disclosures](experiments/breakthrough-groups-context-final-20261020/SUBMISSION-NOTE.md) ·
[Local evidence verification](experiments/breakthrough-groups-context-final-20261020/LOCAL-VERIFICATION.json) ·
[Official source verification](experiments/breakthrough-groups-context-final-20261020/PUBLIC-SOURCE-VERIFICATION.json)

'''
for path,prefix in [('README.md',readme),('docs/AGENT_HANDOFF.md',addition),('docs/research-plan.md',addition)]:
 p=root/path;data=prefix.encode();assert not p.read_bytes().startswith(data);p.write_bytes(data+p.read_bytes());base=git('show','HEAD:'+path);blob=git('hash-object','-w','--stdin',input=data+base).decode().strip();mode=git('ls-tree','HEAD','--',path).decode().split(' ',1)[0];subprocess.run(['git','-C',str(root),'update-index','--add','--cacheinfo',mode+','+blob+','+path],check=True)
dirs=['breakthrough-groups-context-final-20261020','breakthrough-groups-context-finished-20261020','breakthrough-groups-context-development-20261020','breakthrough-groups-context-final-gate-20261020','breakthrough-groups-context-nonce-20261020','breakthrough-groups-safe-context0-20261020','breakthrough-groups-safe-context16-20261020']+['breakthrough-grouped-compact-width-v'+str(i)+'-20261020'for i in range(2,8)]
scripts=['checkpoint-official71.py','CURRENT-ACTIVE.json','phase-compare-compact.rs','prepare-grouped-compact-width.py','prepare-groups-context-finished.py','prepare-groups-context-verification.py','prepare-groups-context-final-controllers.py','prepare-groups-context-packaging.py','collect-groups-context-final.py','prepare-groups-context-official-checks.py','prepare-compact-unitary-tail-v6.py','prepare-compact-fold-compose-v7.py','prepare-cycle4-collection.py','seal-research-cycle4.py','collect-research-cycle4.py','hydrate-submission-evidence.py']
paths=['experiments/'+n for n in dirs]+['experiments/autorun-20261020-breakthrough/'+n for n in scripts]+['experiments/breakthrough-assessment-20261020/snapshots/20261020T170204Z']
subprocess.run(['git','-C',str(root),'add','--',*paths],check=True);allowed=paths+['README.md','docs/AGENT_HANDOFF.md','docs/research-plan.md'];staged=git('diff','--cached','--name-only').decode().splitlines();assert all(any(p==q or p.startswith(q+'/')for q in allowed)for p in staged);assert not any('resource-preflight'in p or'/candidate/'in p or'/observer/'in p or'/tool/'in p or p.endswith('ops.bin')for p in staged);subprocess.run(['git','-C',str(root),'commit','-q','-m','Preserve official T747226 source and evidence; native exact comparator cuts workspace'],check=True);print(git('rev-parse','HEAD').decode().strip())
