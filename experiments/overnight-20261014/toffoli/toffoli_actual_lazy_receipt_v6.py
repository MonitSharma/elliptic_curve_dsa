"""Freeze narrowed fin4 lazy-helper allMR and dirty-scratch qualification."""
import hashlib,json,re
from pathlib import Path

root=Path(__file__).resolve().parents[3];here=Path(__file__).parent
evidence=root/'research-output/overnight-20261014/toffoli/actual-lazy-v6'
native=json.loads((evidence/'receipt/receipt.json').read_bytes());log=(evidence/'run.log').read_text()
assert int((evidence/'run.exit').read_text())==0 and '8 passed; 0 failed' in log
rows=[]
for match in re.finditer(r'TOFFOLI_ACTUAL_LAZY_V6 new=(false|true) emitted=(\d+) executed=(\d+) cases=(\d+) peak=(\d+) critical_mr=(\[[^\n]+?\]) actualdrops=2 freshESH=(\[[^\n]+?\]) zero_free_checks=(\d+)',log):
    new,emitted,executed,cases,peak,mr,esh,frees=match.groups()
    rows.append(dict(new=new=='true',emitted=int(emitted),executed=int(executed),cases=int(cases),peak=int(peak),semantic_MR_indices=json.loads(mr),fresh_ESH_wire_ids=esh,zero_at_free_checkpoints=int(frees)))
assert len(rows)==2 and rows[0]['emitted']+1==rows[1]['emitted'] and rows[0]['executed']==rows[1]['executed']+7*rows[0]['cases']//8
assert rows[0]['zero_at_free_checkpoints']==0 and rows[1]['zero_at_free_checkpoints']==12
proof=re.search(r'TOFFOLI_ACTUAL_LAZY_V6_ALLMR exact_input_cases=(\d+) native_cases=(\d+) max_phase_terms=(\d+) producer_rows=128 raw_bits=18 higher_words=4 room=2 classicalABI=512',log);assert proof
callers=[]
for match in re.finditer(r'TOFFOLI_ACTUAL_LAZY_V6_CALLER cap=(\d+) room=(\d+) tick=(\d+) new=(false|true) hits=(\d+) peak=(\d+) emitted=(\d+) source_caller_resource_only=true',log):
    cap,room,tick,new,hits,peak,emitted=match.groups();callers.append(dict(cap=int(cap),room=int(room),tick=int(tick),new=new=='true',hits=int(hits),peak=int(peak),emitted=int(emitted)))
assert len(callers)==2 and callers[0]['hits']==0 and callers[1]['hits']==1 and callers[0]['emitted']+1==callers[1]['emitted'] and all(row['peak']==1234 for row in callers)
patch=(evidence/'receipt/candidate.patch').read_bytes();assert hashlib.sha256(patch).hexdigest()==native['candidate_patch_sha256']
(here/'actual-lazy-native-v6.patch').write_bytes(patch)
record={'status':'native_top1_direct_nondeep_fin4_drop2_lazy_cleanup_passed_component_only','baseline_revision':native['baseline_revision'],
        'source_sha256':native['source_sha256'],'patch_sha256':native['candidate_patch_sha256'],'pid':int((evidence/'run.pid').read_text()),'exit':0,
        'protected_tracked_changes':native['protected_tracked_changes'],'component_costs':rows,'exact_mean_delta':'-7/8','emitted_CCX_delta':1,
        'exact_allMR':dict(zip(['fixed_input_layout_proofs','native_cases','maximum_phase_terms'],map(int,proof.groups()))),'source_callers_resource_only':callers,
        'classical_scratch_domain':'Every analyzed nb slot initialized with a nonzero rotated dirtyword, including unregistered temporaryslots;512ABI slots retained. This is a specified dirtypattern family, not exhaustive all2^nb initialclassicalassignments.',
        'zero_on_free_proof':'All12 newownedfree checkpoints immediatelyfollow unconditionalBitStore0 atconditionstackdepth0, withc_condition=NO_BIT. Nativeexecutionsplit ateachcheckpointasserts thatbitwordzero for every16semanticMRpattern/inputcase. Originalprefix/lowcarrymeasurementfreebitcontract unchanged.',
        'native_cost_method':'All16semanticC6/T3/Y5/Y3 outcomes uniformlyweighted; sharedprefix seed reset foreachold/new batch. No measurementoutcome selection.',
        'guard_truth_sha256':hashlib.sha256((here/'actual-lazy-guards-v5.json').read_bytes()).hexdigest(),'producer_contract_sha256':hashlib.sha256((here/'actual-esh-contract-v4.json').read_bytes()).hexdigest(),
        'faults_detected':['removedCZ','missingC4_ORbuild','missingfirstTTbuild'],'hashes':{name:hashlib.sha256((evidence/name).read_bytes()).hexdigest() for name in ['run.log','settings.txt','test-binary.sha256','receipt/receipt.json']},
        'limits':'All18 selectedproducerinputs andallMR forfourhigherwords; no genericESH/deep/allhigher wholefold claim. Truebodycaller guard/allocation/cost only, notfullbody arithmetic/phase. No fullqualifiedscore.', 'qualified_score':None}
(here/'actual-lazy-native-v6-receipt.json').write_bytes((json.dumps(record,indent=2)+'\n').encode());print(json.dumps({'status':record['status'],'mean_delta':record['exact_mean_delta'],'allMR':record['exact_allMR']}))
