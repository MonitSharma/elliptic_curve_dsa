"""Freeze exact lazy-helper component mean and allMR evidence."""
import hashlib
import json
from pathlib import Path
import re

root=Path(__file__).resolve().parents[3];here=Path(__file__).parent
evidence=root/'research-output/overnight-20261014/toffoli/actual-lazy-v5'
native=json.loads((evidence/'receipt/receipt.json').read_bytes());log=(evidence/'run.log').read_text()
assert int((evidence/'run.exit').read_text())==0 and '8 passed; 0 failed' in log
rows=[]
for match in re.finditer(r'TOFFOLI_ACTUAL_LAZY_LOG_COMPONENT room=(\d+) new=(false|true) emitted=(\d+) executed=(\d+) cases=(\d+) peak=(\d+) hits=(\d+) critical_mr=([^\n]+)',log):
    room,new,*values,indices=match.groups()
    rows.append(dict(room=int(room),new=new=='true',**dict(zip(['emitted','executed','cases','peak','hits'],map(int,values))),semantic_MR_indices=json.loads(indices)))
assert len(rows)==2 and rows[0]['emitted']+1==rows[1]['emitted']
assert rows[0]['executed']==rows[1]['executed']+7*rows[0]['cases']//8
proof=re.search(r'TOFFOLI_ACTUAL_LAZY_LOG_ALLMR exact_input_cases=(\d+) native_cases=(\d+) max_phase_terms=(\d+) max_quantum_terms=(\d+)',log);assert proof
callers=[]
for match in re.finditer(r'TOFFOLI_ACTUAL_LAZY_LOG_CALLER cap=(\d+) room=(\d+) tick=(\d+) new=(false|true) hits=(\d+) peak=(\d+) emitted=(\d+) source_caller_resource_only=true',log):
    cap,room,tick,new,hits,peak,emitted=match.groups();callers.append(dict(cap=int(cap),room=int(room),tick=int(tick),new=new=='true',hits=int(hits),peak=int(peak),emitted=int(emitted)))
assert len(callers)==2 and callers[0]['hits']==0 and callers[1]['hits']==1 and callers[0]['emitted']+1==callers[1]['emitted']
patch=(evidence/'receipt/candidate.patch').read_bytes();assert hashlib.sha256(patch).hexdigest()==native['candidate_patch_sha256']
(here/'actual-lazy-native-v5.patch').write_bytes(patch)
record={'status':'native_fin3_drop1_lazyC4_TT_passed_component_only','baseline_revision':native['baseline_revision'],
        'source_sha256':native['source_sha256'],'patch_sha256':native['candidate_patch_sha256'],'pid':int((evidence/'run.pid').read_text()),'exit':0,
        'protected_tracked_changes':native['protected_tracked_changes'],'component_costs':rows,
        'exact_mean_delta':'-7/8','emitted_CCX_delta':1,'mean_method':'All16 equallyweighted semanticC6/T3/Y5/Y3 independentMR patterns forced for eachnative inputbatch; unchanged sharedprefix outcomes seeded identically. No outcome selection.',
        'exact_allMR':dict(zip(['fixed_input_layout_proofs','native_cases','maximum_phase_terms','maximum_quantum_terms'],map(int,proof.groups()))),
        'source_callers_resource_only':callers,'guard_truth_sha256':hashlib.sha256((here/'actual-lazy-guards-v5.json').read_bytes()).hexdigest(),
        'faults_detected':['removedCZ','removedC4_ORbuild','removedfirstTTbuild'],
        'hashes':{name:hashlib.sha256((evidence/name).read_bytes()).hexdigest() for name in ['run.log','settings.txt','test-binary.sha256','receipt/receipt.json']},
        'scope':'fin3/drop1,all14primitiveinputs,fourhigherwords,room3,oneactualdrop,everyq/dirty512classABI/incomingphase; storedOR guards and mutablepersistentTTneed allMRproved.',
        'classical_ownership':'Persistentneed/complement and ownedstandaloneHMR bits explicitlycleared beforefree. Originalsharedprefix/lowcarry helpermeasurement bits retainbaselinefreebit semantics. ABI512bits checkedunchanged; no allscratchclassicalzero claim.',
        'limits':'No fin4/deep transfer orfullbody arithmetic/phase claim. Finitehigherwords notallhigherfold proof. Completecomponent meanonly; no wholepointaddition record.', 'qualified_score':None}
(here/'actual-lazy-native-v5-receipt.json').write_bytes((json.dumps(record,indent=2)+'\n').encode())
print(json.dumps({'status':record['status'],'mean_delta':record['exact_mean_delta'],'allMR':record['exact_allMR']}))
