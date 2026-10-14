"""Archive compact source-bound model and conditional-phase evidence."""
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
RAW=ROOT/'research-output/overnight-20261014'

def write(name,value):
    (HERE/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')

result=json.loads((RAW/'qubit-capacity-result.json').read_text())
assert all(not v for v in result['flagged'].values())
assert result['script_sha256']==hashlib.sha256((HERE/'capacity-screen-v1.py').read_bytes()).hexdigest()
result.update(status='PASS_IDEAL_MODEL_ONLY',pid=2457123,exit_code=0,
    server_directory='/home/hclau/ecdsa_research/overnight-20261014/coordinator-qubit-capacity',
    log_sha256='8d454c37787652b5674210245bd65f0f3e60709a304796ed6c4c4eb473627175',
    preserved_executed_source='capacity-screen-v1.py',
    physical_map_third_owner='PENDING; integer geometry does not prove a clean physical lane',
    negative_controls='Four local regression tests agree with original six public source-model failures, require reserve9 and detect the original QB23 cap failure')
write('capacity-screen-receipt.json',result)

log=(RAW/'qubit-phase-v3.log').read_text()
source=json.loads((HERE/'qubit-phase-v3-source.json').read_text())
proofs=[dict(zip(['ops','measurement_variables','maximum_phase_terms','maximum_quantum_terms'],map(int,m)))for m in re.findall(r'CONDITIONAL_PHASE_PROOF ops=(\d+) input_lanes=64 measurement_variables=(\d+) maximum_phase_terms=(\d+) maximum_quantum_terms=(\d+)',log)]
assert len(proofs)==38,len(proofs)
assert log.count('inconclusive: XOR term cap')==2
write('conditional-phase-audit-receipt.json',{
    'status':'PARTIAL_EXACT_PROOF_WITH_TWO_INCONCLUSIVE_SUPPORT_LIMITS','qualified_score':None,
    'kernel':{'scope':'Exact Boolean ANF for all independently indexed R/HMR outcomes on fixed64-lane basis-input packets; not a universal input proof','source':'phase-polynomial-v1.rs','sha256':source['kernel_sha256'],'native_tests':4,'native_tests_exit':0,'native_test_pid':2423409,'native_log_sha256':'e7e858337a5935700da24e65a0d823fe28bdea00014a173a35fa1d5a094e6017'},
    'source':source,'pid':2446538,'exit_code':101,'elapsed_seconds':86.96,'peak_RSS_KiB':843360,
    'server_directory':'/home/hclau/ecdsa_research/overnight-20261014/coordinator-qubit-phase-v3',
    'log_sha256':hashlib.sha256((RAW/'qubit-phase-v3.log').read_bytes()).hexdigest(),
    'passes':['3713reserve9payload256lanes forward/inverse','q23SWpreposition256dirtylanes forward/inverse','first11of13no-payloadcolumns64lanes each forward/inverse'],
    'inconclusive':['8048payload proof exceeds8192 ANF support','12thno-payloadcolumn exceeds8192 ANF support;13thnotreached'],
    'proof_instances':proofs,'source_generator':'qubit-phase-generator-v3.py',
    'preserved_earlier_failures':{'v1_pid':2431796,'v1_exit':1,'v1_reason':'External generator asserted wrong insertion count; no simulation','v2_pid':2438634,'v2_exit':101,'v2_reason':'External crate omitted public serializer write_ops; no simulation'},
    'new_kernel_retry':{'kernel_sha256':'d41de327f9e2162d8009235c77780f3a996351d57aed2011497ee1c6b5e4f035','native_test_pid':2461533,'native_tests':4,'exit_code':0,'log_sha256':'ffc32fb358ea0ab7e9badd31d5e90a393f28dee30030d8dd607a7bae465720bf','compile_only_failure':{'pid':2459670,'exit_code':101,'source':'phase-polynomial-v2-compile-failed.rs','log_sha256':'e181f1b102baf6efa6792524b888a3db5dbad46c9a0c2d5e837d52463c209f6f'}},
    'PH_owner_source_retry':{'pid':2463821,'exit_code':101,'source':'qubit-phase-v4-source.json','log_sha256':'2a0f891bc2ba77ab2b85b722c3f6846f33ca29c87894003def395cf416b40648','native_test_status':'3passed3inconclusive','passes':['both one-owner and two-owner dirty preposition fixtures','3713reserve9payload256lanes','first11no-payloadcolumns'],'inconclusive':['8048payload and independent structuredq22payload at Hmr operation840622','12thno-payloadcolumn at Hmr operation2073727;13thnotreached'],'diagnosis':'Classical-slot conditional Hmr assignment exceedsANFsupport; prior phase maximum1 and prior quantum maximum2. No nonzero-phase or quantum-value failure follows from support limits.'},
    'protected_source_modified':False})
