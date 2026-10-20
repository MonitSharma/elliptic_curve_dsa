import json,subprocess
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[2];a=Path(__file__).resolve().parent
def git(*args):return subprocess.check_output(['git','-C',str(root),*args])
assert not git('diff','--cached','--name-only').strip()
names=['breakthrough-context16384-lease-20261020','breakthrough-exact-native-ports-v3-20261020','breakthrough-exact-ports-development-20261020','breakthrough-native-both-finished-20261020','breakthrough-stackv3-width-20261020','breakthrough-stackv3-width-lean128-20261020','breakthrough-stackv3-width-loan128-20261020','breakthrough-stackv3-width-stats-20261020','breakthrough-stackv3-width-loan-drop130-20261020','breakthrough-stackv3-width-plan7-20261020','breakthrough-stackv3-plan7-stats-20261020']
verified={n:json.loads((root/'experiments'/n/'LOCAL-VERIFICATION.json').read_text())['members']for n in names}
state=json.loads((a/'CURRENT-1020-1340.json').read_text());state.update(at_utc=datetime.now(timezone.utc).isoformat(),last_root_commit=git('rev-parse','HEAD').decode().strip(),verified_completed_research_evidence=verified)
state['public_records_snapshot']='experiments/breakthrough-assessment-20261020/snapshots/20261020T140949Z'
state['current_width_record']={'Q':670,'T':557860556,'id':'e2e13cf3-6711-4a39-8a24-b3ddda56f56c','source':'216b81b4397bd8de111de6b04c779dad174099bb'}
state['active_job']={'directory':'breakthrough-stackv3-width-plan7-range-20261020','pid':2871774,'status':'Four native controls PASS; build complete; fullpublic714c then fixedraw construction running.','scope':'Exact carryloan128 and separately native-verified50bit/budget7 ladder; requestdrop3 onforward130..137 onlylowerbudget, stronger28-bit witness. All old guards unchanged. No finalgate/nonce/benchmark/score.','if_fits':'Measure actualQ, freeze full raw/generic bindings, verify fresh512x64 development before any final gate.','if_fails':'Preserve precise next guard; use supported native identities or start read-only classical-at-peak/carry-pebble audit; no guard/table weakening.'}
state['completed_to_preserve']+=['All eleven completed diagnostic fronts locally hydrated: '+str(sum(verified.values()))+' individually hashed members.','loan-drop130=2 duplicates existingSL_N2_DROPN=2 and has no effect; prior closed-ripple explanation incorrect.','plan7 native4 PASS including65536 full50bit affine lanes and deliberatephasefault;1233 passes130 thenstops131,1232 stops127. Static successfulrawQ1234 only.','plan7 stats verifies protected analyzer; publicQ1234/proxy755408.75,raw28Q1234/proxy756104.0; proxy is NOT executedmean or scoredT.']
(a/'CURRENT-1020-1415.json').write_text(json.dumps(state,indent=2)+'\n')
scripts=['collect-front-evidence.py','prepare-plan7-stats.py','prepare-stack-loan-drop.py','prepare-stack-plan7.py','seal-front-evidence.py','prepare-stack-plan7-range.py','prepare-plan7-preservation.py','seal-plan7-evidence.py','collect-plan7-evidence.py','checkpoint-plan7-research.py','CURRENT-1020-1415.json']
paths=['experiments/'+n for n in names]+['experiments/breakthrough-stackv3-width-plan7-range-20261020']+['experiments/autorun-20261020-breakthrough/'+n for n in scripts]
paths+=['experiments/breakthrough-assessment-20261020/snapshots/20261020T140949Z/'+n for n in ['.gitattributes','leader-product.json','leader-qubits.json','leader-toffoli.json','PUBLIC-RECORDS.json','public-submissions.json.gz','SNAPSHOT-MANIFEST.json']]
subprocess.run(['git','-C',str(root),'add','--',*paths],check=True)
staged=git('diff','--cached','--name-only').decode().splitlines();assert all(any(p==q or p.startswith(q+'/')for q in paths)for p in staged)
assert not any('resource-preflight' in p or '/observer/' in p or '/candidate/' in p or p.endswith('ops.bin')for p in staged)
subprocess.run(['git','-C',str(root),'commit','-q','-m','Preserve exact carry-plan width research and verified diagnostic evidence'],check=True)
print(json.dumps({'verified_members':sum(verified.values()),'fronts':len(names),'commit':git('rev-parse','HEAD').decode().strip(),'scope':'Research only. Product goal remains active.'}))
