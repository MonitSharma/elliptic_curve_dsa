"""Preserve allocator equality separately from failed extended-domain checks."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

HERE=Path(__file__).parent
AREA=HERE.parents[2]/'research-output/overnight-20261014/toffoli'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,obj):HERE.joinpath(name).write_bytes((json.dumps(obj,indent=2)+'\n').encode())

def main():
    path=AREA/'allocator-v2r2.log';log=path.read_text();assert '3 passed; 0 failed' in log
    native=[];equal=[];references=[]
    for line in log.splitlines():
        if line.startswith('TOFFOLI_ALLOCATOR_NATIVE'):native.append(dict(re.findall(r'(\w+)=([^ ]+)',line)))
        if line.startswith('TOFFOLI_ALLOCATOR_EQUAL'):equal.append(dict(re.findall(r'(\w+)=([^ ]+)',line)))
        if line.startswith('TOFFOLI_EXTENDED_DOMAIN_REFERENCE'):references.append(dict(re.findall(r'(\w+)=([^ ]+)',line)))
    assert len(native)==110 and len(equal)==55
    assert all(int(r['reference_bad'])==32 for r in native)
    assert sum(int(r['phase_bad']) for r in native)==5249
    source=json.loads(HERE.joinpath('bank-product-allocator-v2-source.json').read_text())
    assert source['protected_tracked_changes']==[]
    save('allocator-v2-native-receipt.json',{
        'status':'allocator_and_disabled_gate_identity_passed; paired_extended_domain_values_passed; reference_and_phase_checks_failed_unadmitted',
        'pid':2428955,'exit':0,'test_count':3,'exact_allocator_pairs':55,'disabled_bank_exact_operation_vector_pairs':55,
        'paired_native_cases':56320,'native_low_input_contract':'Independent 256-bit field payload pairs/all32 tape letters, including0/1/P-1; actual producer reachability unproved.',
        'reference_mismatches_total':3520,'sampled_phase_failures_total':5249,'phase_pass':False,
        'rows':native,'allocator_rows':equal,'first_reference_counterexample':references[0],
        'native_invariants':'Old/new complete output vectors equal for all pairs. Source, control letters, spectator padding and scratch checked. Both old/new fail the separate reference/phase diagnostics on the preserved extended domain.',
        'log_sha256':sha(path),'settings_sha256':sha(AREA/'allocator-v2r2.settings'),
        'test_binary_receipt_sha256':sha(AREA/'allocator-v2r2-binary.sha256'),
        'candidate_patch_sha256':source['candidate_patch_sha256'],'source_receipt':source,
        'operational_contexts_preserved':['Y15_CARRY_IN','Y17_EXTRA','REPLAY_SIGN_LOANS','HEO_CMP_SHIFT','HEO_TIE','PHASE_CAP','C35_AT','C35_CMP_FX','C35_PADS','Y16_FOLD','Y16_ACC','Y16_NEST','Y17_LOG','Y28_COUNT','PAYLOAD_AT','LOAN_ACTIVE','bank MODE/HEAD_PLAN'],
        'deferred_storage':'Replay excludes tick0; original Y26_T0=5 unchanged. Original y42 allocator assertions/tables and binary gate rewrite tables unchanged.',
        'limitations':'Successful test status applies to allocator equality, disabled-bank operation equality and paired native values only. Extended-domain reference and sampled phase diagnostics explicitly fail; this is not body-phase qualification, producer admission or a full-circuit resource record.',
        'failed_attempts':[{'job':'allocator-v2','exit':101,'status':'fixture prime import compilation failure','log_sha256':sha(AREA/'allocator-v2-failed-compile.log')},
                           {'job':'allocator-v2r1','pid':2422812,'exit':101,'status':'false Y26_T0=0 guard and preserved first extended-domain reference failure','log_sha256':sha(AREA/'allocator-v2r1-failed.log')}]
    })
    raw=AREA/'toffoli-outside-direction-v1r1-20261014.json';d=json.loads(raw.read_text())
    save('outside-direction-v1-summary.json',{
        'status':d['status'],'source_lf_sha256':d['source_lf_sha256'],'netlist_sha256':d['netlist_sha256'],
        'domain_rows':d['domain_rows'],'old_function_span_rank':46,'selected_interface_rank':45,
        'selected_raw_pairs':[[4,13],[4,14],[5,13],[5,14],[6,13],[6,14]],
        'interfaces':90,'status_counts':dict(Counter(x['status'] for x in d['examined'])),
        'seconds':d['seconds'],'raw_receipt_sha256':sha(raw),'raw_receipt_bytes':raw.stat().st_size,
        'log_sha256':sha(AREA/'toffoli-outside-direction-v1r1-20261014.log'),
        'settings_sha256':sha(AREA/'toffoli-outside-direction-v1r1-20261014.settings'),
        'limits':d['limits'],'scope':d['scope'],
        'next':'Permit four-dimensional linear combinations of the six old temporary directions, rather than only15 coordinate subsets; these are651 subspaces per selected outside function.'})
    print('frozen allocator v2 receipt; extended-domain phase/reference explicitly failed')

if __name__=='__main__':main()
