"""Freeze completed bank-width rejection and allocator integration evidence."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re

HERE=Path(__file__).parent
AREA=HERE.parents[2]/'research-output/overnight-20261014/toffoli'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,data):HERE.joinpath(name).write_bytes((json.dumps(data,indent=2)+'\n').encode())

def main():
    v3=AREA/'allocator-v3r1';log=v3.joinpath('run.log').read_text();assert '3 passed; 0 failed' in log
    equal=[dict(re.findall(r'(\w+)=([^ ]+)',line)) for line in log.splitlines() if line.startswith('TOFFOLI_ALLOCATOR_EQUAL')]
    native=[dict(re.findall(r'(\w+)=([^ ]+)',line)) for line in log.splitlines() if line.startswith('TOFFOLI_ALLOCATOR_NATIVE')]
    assert len(equal)==110 and len(native)==110
    source=json.loads(v3.joinpath('receipt.json').read_text());assert source['protected_tracked_changes']==[]
    HERE.joinpath('bank-product-allocator-v3.patch').write_bytes(v3.joinpath('candidate.patch').read_bytes())
    save('bank-product-allocator-v3-source.json',source)
    save('allocator-v3-native-receipt.json',{
        'status':'110 allocator+disabled-gate equality pairs passed; extended-domain reference/phase FAILED_unadmitted',
        'pid':2444693,'exit':0,'native_tests_passed':3,'primed_and_unprimed_allocator_pairs':110,
        'disabled_bank_exact_operation_vector_pairs':110,'paired_native_field_cases':56320,
        'extended_domain_reference_mismatches':sum(int(r['reference_bad']) for r in native),
        'extended_domain_sampled_phase_failures':sum(int(r['phase_bad']) for r in native),'body_phase_pass':False,
        'allocator_rows':equal,'extended_domain_rows':native,
        'candidate_patch_sha256':source['candidate_patch_sha256'],'protected_changes':[],
        'log_sha256':sha(v3/'run.log'),'settings_sha256':sha(v3/'settings.txt'),'test_binary_receipt_sha256':sha(v3/'test-binary.sha256'),
        'method':'Original-body private emission from identical allocator input determines exact baseline ordering; actual post-body scratch pool equals initial free IDs plus the original fresh frontier. IDs omitted by the optimized body were never touched and are added as clean allocator metadata only. Existing y42 ownership/set assertions and all historical tables remain unchanged.',
        'limits':'Value equality and spectators/scratch pass on the preserved independent extended domain. Its source-to-reference and sampled phase checks fail on both old/new sides; actual producer admission is unproved. No full benchmark, complete builder stream or scored count.',
        'failed_compile_attempt':{'pid':2441992,'exit':101,'status':'missing frontier argument; source/log preserved server allocator-v3/prelaunch and allocator-v3/run.log'}})
    failed=AREA/'builder-v2';terminal=json.loads(failed.joinpath('receipt.json').read_text())
    save('bank-product-failed-builder-v2.json',{
        'status':'failed_original_scratch_set_assertion_before_complete_stream','pid':2436425,'exit':101,
        'candidate_patch_sha256':terminal['candidate_patch_sha256'],'protected_changes':[],
        'failure':'Early payload creates legitimate fresh IDs1228..1230; v2 restore compared post-body set to pre-body set without extending fresh frontier.',
        'native_fixture_gap':'V2 only primed its free pool; v3 separately covers primed and fresh-frontier cases.',
        'log_sha256':sha(failed/'run.log'),'settings_sha256':sha(failed/'settings.txt'),'builder_binary_receipt_sha256':sha(failed/'builder.sha256'),
        'terminal_receipt':terminal,'complete_peak':None,'complete_gate_count':None,'complete_stream_sha256':None})
    paths=['allocator-v2-native-receipt.json','allocator-v3-native-receipt.json','bank-product-allocator-v2.patch','bank-product-allocator-v2-source.json',
           'bank-product-allocator-v3.patch','bank-product-allocator-v3-source.json','bank-product-failed-builder-v2.json',
           'bank-table-width-obstruction.json','outside-direction-v1-summary.json','phase-closed-interface-v1.json','phase-upper-extension-v1.json']
    save('third-checkpoint-receipt.json',{
        'collected_at_utc':datetime.now(timezone.utc).isoformat(),'baseline_revision':'c5bb1ec876db859a3f9f8a9052c140a145df834e',
        'status':'bank-only PRODUCT width route closed by retained table floor; no complete full-stream count or new record',
        'qualified_score':None,'completed_files_sha256':{name:sha(HERE/name) for name in paths},
        'active_solver':{'pid':2451609,'family':'all651 rank4 old-temporary subspaces with chosen outside acc3*k1','status':'pending','limit_seconds':900,'vmem_KiB':2097152,'cores':1,
                         'server_root':'/home/hclau/ecdsa_research/overnight-20261014/toffoli','name':'toffoli-external-planes-v2-20261014'},
        'scope':'Component costs/proofs and integration failures only. Upper tensor obstruction concerns unrestricted constructor inputs with free quadratic phase cleanup; it is not a complete point-addition proof. Full-body extended-domain reference/phase remains failed and unadmitted.'})
    print('third checkpoint frozen; bank-only width route closed, solver pending')

if __name__=='__main__':main()
