import ast,json,subprocess
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[2];a=Path(__file__).resolve().parent
def git(*args,input=None):return subprocess.check_output(['git','-C',str(root),*args],input=input)
assert not git('diff','--cached','--name-only').strip();tree=ast.parse((a/'seal-research-cycle2.py').read_text());names=ast.literal_eval(next(x.value for x in tree.body if isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='names'for t in x.targets)));verified={n:json.loads((root/'experiments'/n/'LOCAL-VERIFICATION.json').read_text())['members']for n in names}
state=json.loads((a/'CURRENT-1020-1415.json').read_text());state.update(at_utc=datetime.now(timezone.utc).isoformat(),last_root_commit=git('rev-parse','HEAD').decode().strip(),cycle2_verified_completed_evidence=verified)
state['active_jobs']=[{'directory':'breakthrough-public-e3-live-finished-20261020','pid':2904654,'status':'COMPLETE native2/proof9+6, canonical1063c1fd equals independent tool, actualQ1234,11603148ops, nonce0c9f9f2fc, diagnostic755353.5 is NOT scoredT.'},{'directory':'breakthrough-public-e3-live-development-20261020','pid':2905358,'status':'Fresh512x64 three-source full outputs, strict cache53/parity equality, waitDEVELOPMENT-CONTROLLER.exit.'},{'directory':'breakthrough-public-e3-live-final-gate-20261020','pid':2906110,'status':'Wait strictdevelopment, then freshpublicproduct parent check and SOLE32768x64 public-e3-cache53-live7-final-20261020-v1. Verdict final; PASS only nonce/benchmark/autosubmit.'},{'directory':'breakthrough-live-products-absorption-v2-20261020','pid':2897179,'status':'Native6 PASS incl exhaustiveBoolean256 truth tests. Fixedcache53 firstscan7 provedparities, public7, remaininggeneric1233/T748691 scans ongoing. No new scored record.'},{'directory':'breakthrough-native-both-context16-20261020','pid':2907170,'status':'IndependentT target officiald182/Q1464/T748691; fixedexactcontext16384 with16 extra donors <=Q1480, native7 precedecomponent. Not gated or scored.'}]
state['active_job']=state['active_jobs'][2]
state['cycle2_conclusions']={'width1233':'Exactloan128 plus independently native-verifiedseven-helper plan atforward130..137/reverse124..127 constructs actualQ1233 stronger28 witness; generic14controls. Fresh512: mean757702.2428 vs parent756477.9651;54samevaluefails,zero dirty,36jointfailure targetdifferences. Zeroaddedwirecontext117 and contextzero extension117 do not close product gap; no finalgate/nonce.','public_cache53':'Native9proofcontrols,53leases existingIDs<=1229. Pure fullparent714c+cacheoutput bindings, checkedhistoricaltail,nonce0. Candidateallunit18pass/2fail vs exactGit88869 control17pass/same2fail, samewrongdivisioninput, profilingNotPresent; isolatedcachetestPASS. Originalfailures retained; resumedexit0. Fullfresh512: values65sameIDs, no target/ancilladifferences, phase46parent/43candidate,failed70/71, executedmeans756479.6456/756424.5381. Development only, notfinalgate/score.','generalpass':'Exactfull-original-op symbolic productparity, Gaussian sparseclosure, no newRNG/qubits/classical changes.96termpass native5 provespublic6/generic3/T0.512termproductimplication pass native6 provespublic7/cache7 sofar. Nativefixture/parser failures all retained separately.','classicalaudit':'Read-only taint/idle-slot nominations only; no widthlowerbound or rewrite. Public781/223 and stronger785/227; exactbranchcofactoring837/279 and841/283. All558 longuncoveredintervals remain.','provenance':'18 newly hydrated fronts,476 members; previous11 fronts482 members. No new scored point inREADME/plots. OfficialT748691 and product933497554 standing unchanged pending freshgate refresh.'}
(a/'CURRENT-1020-1510.json').write_text(json.dumps(state,indent=2)+'\n')
addition='''## 20 October 2026, 23:10 SGT: product candidate at final-gate boundary

Keep the active global product goal unfinished. Auto-submit every newly verified
current-record improvement as GPT-6 sol/Codex; no further approval question.
OfficialT748691/d182 remains our latest result. New directpublice3 cache53 plus
seven independently proved liveparity replacements builds actualQ1234,11603148
ops, canonical1063c1fd, nonce0streamc9f9f2fc. This is NOT a benchmark record.
Full source frozen8daae54f; all parent714c/cache/output records bound, no old
table change. Cacheproof9 plus compiler6 native controls, newruntime2 PASS.
Two original isolated unit failures exactly reproduce on unmodifiedGit88869
(profile NotPresent; same isolatedapproxdivision1/1024); all logs retained.

Active product jobs: finished2904654 complete; development2905358 must prove
cache53 vs parity fullvalue/phase/ancilla equality; finalgate2906110 waits it,
then refreshes exact current product parent and declares SOLE32768x64 label
public-e3-cache53-live7-final-20261020-v1. NEVER rerun a failed gate. PASS only
permits qualifiedascendingnonce, unchangedbenchmark, localreview and auto-upload.
NativeT context16 component2907170 separately targets currentofficiald182 at
<=Q1480; own freshT gate required. Generalexactproof2897179 remains running.

ActualQ1233 native plan works but complete developmentalT757702 is too costly;
117 existing-wire exactleases do not close gap. No gate/nonce on that line.
Read experiments/autorun-20261020-breakthrough/CURRENT-1020-1510.json for all
new hashes/jobs and inherited-failure audit. 18newfronts476 members hydrated,
prior11fronts482 members preserved; source/patch/failures intact. Preserve all
preexisting root/submodule/user edits and unrelated server QOB jobs.

'''
for path in['docs/AGENT_HANDOFF.md','docs/research-plan.md']:
 p=root/path;data=addition.encode();p.write_bytes(data+p.read_bytes());base=git('show','HEAD:'+path);blob=git('hash-object','-w','--stdin',input=data+base).decode().strip();mode=git('ls-tree','HEAD','--',path).decode().split(' ',1)[0];subprocess.run(['git','-C',str(root),'update-index','--add','--cacheinfo',mode+','+blob+','+path],check=True)
scripts=['prepare-stack-plan7-both.py','prepare-plan7-both-stats.py','prepare-stack-plan7-generic.py','prepare-stack-plan7-generic-v2.py','prepare-classical-width-audit.py','prepare-classical-width-audit-v2.py','prepare-plan7-zero-donors.py','prepare-plan7-development.py','prepare-context-clean-donors.py','prepare-public-e3-context-clean.py','prepare-public-e3-finished.py','prepare-public-e3-finished-v2.py','prepare-public-e3-test-audit.py','prepare-public-e3-development.py','prepare-public-e3-development-v2.py','prepare-live-products.py','prepare-live-products-v2.py','prepare-live-products-absorption.py','prepare-live-products-absorption-v2.py','prepare-public-e3-live-finished.py','prepare-public-e3-live-development.py','prepare-public-e3-final-gate.py','prepare-native-both-context16.py','seal-research-cycle2.py','prepare-cycle2-collection.py','run-seal-cycle2.py','collect-research-cycle2.py','checkpoint-cycle2.py','CURRENT-1020-1510.json']
active=['breakthrough-live-products-absorption-v2-20261020','breakthrough-public-e3-live-finished-20261020','breakthrough-public-e3-live-development-20261020','breakthrough-public-e3-live-final-gate-20261020','breakthrough-native-both-context16-20261020']
paths=['experiments/'+n for n in names+active]+['experiments/autorun-20261020-breakthrough/'+n for n in scripts];subprocess.run(['git','-C',str(root),'add','--',*paths],check=True);allowed=paths+['docs/AGENT_HANDOFF.md','docs/research-plan.md'];staged=git('diff','--cached','--name-only').decode().splitlines();assert all(any(p==q or p.startswith(q+'/')for q in allowed)for p in staged);assert not any('resource-preflight'in p or'/candidate/'in p or'/tool/'in p or'/unmodified-control/'in p or p.endswith('ops.bin')for p in staged);subprocess.run(['git','-C',str(root),'commit','-q','-m','Preserve verified exact product candidates, inherited failures, and autonomous gate plan'],check=True);print(json.dumps({'commit':git('rev-parse','HEAD').decode().strip(),'new_fronts':len(names),'verified_members':sum(verified.values()),'scope':'No new scored record; active gate and T research continue.'}))
