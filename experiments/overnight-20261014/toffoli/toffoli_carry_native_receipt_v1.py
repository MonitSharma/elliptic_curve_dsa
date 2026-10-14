"""Freeze positive/failed native carry cleanup evidence without score claims."""
import hashlib
import json
from pathlib import Path
import re

root=Path(__file__).resolve().parents[3];here=Path(__file__).parent
area=root/'research-output/overnight-20261014/toffoli';evidence=area/'carry-cleanup-v1r2'
source=json.loads((evidence/'receipt/receipt.json').read_bytes());log=(evidence/'run.log').read_text()
assert int((evidence/'run.exit').read_text())==0 and '3 passed; 0 failed' in log
rows=[]
for match in re.finditer(r'TOFFOLI_CARRY_COMPONENT room=(\d+) shots=(\d+) old_emitted=(\d+) new_emitted=(\d+) old_executed=(\d+) new_executed=(\d+) old_peak=(\d+) new_peak=(\d+) hits=(\d+)',log):
    values=list(map(int,match.groups()));item=dict(zip(['room','shots','old_emitted','new_emitted','old_executed','new_executed','old_peak','new_peak','hits'],values))
    assert item['hits']==1 and item['old_emitted']==item['new_emitted']+1
    assert item['old_executed']==item['new_executed']+item['shots'];rows.append(item)
phase=[]
for match in re.finditer(r'TOFFOLI_NATIVE width=(\d+) fin=(\d+) measurements=(\d+) high_words=(\d+) checked_coefficients=true cases=(\d+) ops=(\d+)',log):
    phase.append(dict(zip(['width','fin','measurements','upper_words','cases','ops'],map(int,match.groups()))))
assert len(rows)==7 and len(phase)==2
failed=[]
for name,status in [('v1','compile_only_QubitId_hash_assertion_failed'),('v1r1','fixture_phase_structure_and_unmatched_rng_cost_assertions_failed')]:
    path=area/f'carry-cleanup-{name}';record=json.loads((path/'receipt/receipt.json').read_bytes())
    failed.append({'version':name,'status':status,'exit':int((path/'run.exit').read_text()),
                   'pid':int((path/'run.pid').read_text()),'source_sha256':record['source_sha256'],
                   'candidate_patch_sha256':record['candidate_patch_sha256'],'log_sha256':hashlib.sha256((path/'run.log').read_bytes()).hexdigest(),
                   'all_inputs_or_all_measurements_passed':False})
patch=(evidence/'receipt/candidate.patch').read_bytes();assert hashlib.sha256(patch).hexdigest()==source['candidate_patch_sha256']
(here/'carry-cleanup-native-v1r2.patch').write_bytes(patch)
result={'status':'native_changed_carry_cleanup_passed_component_only_current_fullguard_zero',
        'baseline_revision':source['baseline_revision'],'source_sha256':source['source_sha256'],
        'candidate_patch_sha256':source['candidate_patch_sha256'],'pid':int((evidence/'run.pid').read_text()),'exit':0,
        'protected_tracked_changes':source['protected_tracked_changes'],'phase_fixtures':phase,'paired_cost_fixtures':rows,
        'total_positive_native_cases':sum(item['cases'] for item in phase)+sum(2*item['shots'] for item in rows),
        'phase_structure':'No nested/direct multipliedMR guards; each conditioned linear block independently restores all symbolicqubits, so its phase is affineinMR. Zeroand everyMR coefficient checked for both tested38upperword layouts.',
        'fault_control':'Removed finalCZ detected innew cleanup fixture; negative testpassed.',
        'test_seconds':38.68,'wall_seconds':128.80,'peak_rss_KiB':1195984,
        'hashes':{name:hashlib.sha256((evidence/name).read_bytes()).hexdigest() for name in ['run.log','settings.txt','test-binary.sha256','receipt/receipt.json']},
        'failed_versions':failed,
        'fullrecord':None,'current_c5_fullguard_occurrences':0,
        'limits':'OneANDsaving is only per guarded component relativeto shippedloan. Testedupperwords do not alone prove everyupperinput. Independent low-domain polynomial/rebase identity appliesat its explicitbank boundary; expandedearlyloan changesladderplans and needsproducer/completequalification. No fullresource record fromthis fixture.'}
(here/'carry-cleanup-native-v1r2-receipt.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
print(json.dumps({'status':result['status'],'positive_native_cases':result['total_positive_native_cases'],'patch_sha256':result['candidate_patch_sha256']}))
