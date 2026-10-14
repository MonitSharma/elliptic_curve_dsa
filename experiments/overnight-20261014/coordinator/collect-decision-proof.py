"""Preserve exact fixed-input/all-measurement phase checks, without scores."""
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
RAW=ROOT/'research-output/overnight-20261014'
kernel=ROOT/'scripts/phase_decision_diagram.rs'
assert hashlib.sha256(kernel.read_bytes()).hexdigest()=='72ab93a2fa1fd20bb3aad370aca9f6016ea9069013eaaa34d6b02d911d859622'
receipts={}
for name,pid,tests in [('q693-v2',2493295,6),('n275-v2',2495284,9)]:
    log=RAW/f'qubit-decision-{name}.log';text=log.read_text()
    assert f'test result: ok. {tests} passed; 0 failed' in text
    assert 'inconclusive:' not in text and 'panicked' not in text
    instances=[dict(zip(['ops','measurement_variables','maximum_phase_size_bound','maximum_quantum_size_bound'],map(int,m)))for m in re.findall(r'DECISION_DIAGRAM_PHASE_PROOF ops=(\d+) input_lanes=64 measurement_variables=(\d+) maximum_phase_size_bound=(\d+) maximum_quantum_size_bound=(\d+)',text)]
    source=json.loads((HERE/f'qubit-decision-{name}-source.json').read_text())
    receipts[name]={'status':'PASS_FIXED_INPUT_ALL_MEASUREMENT_PHASE_AND_FINAL_QUANTUM_STATE','pid':pid,'exit_code':0,'selected_tests':tests,'source':source,'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest(),'proof_instances':instances,'server_directory':f'/home/hclau/ecdsa_research/overnight-20261014/coordinator-qubit-decision-{name}',
        'limitations':'Finite component inputs only, including forward/inverse; does not prove all curve points or full-circuit width/correctness. Classical measurement scratch need not clear. No scored result.',
        'peak_RSS_KiB':863728 if name=='q693-v2' else 1082272,
        'elapsed_seconds':None if name=='q693-v2' else 109.80}
out={'qualified_score':None,'scope':'Canonical reduced ordered decision diagrams with u64 masks; all independently indexed R/Hmr outcomes on each fixed input lane. All18 operation types, mutable classical slots and condition snapshots retained exactly.',
    'kernel_sha256':hashlib.sha256(kernel.read_bytes()).hexdigest(),'kernel_source':'../../../scripts/phase_decision_diagram.rs',
    'native_kernel_validation':{'pid':2488614,'exit_code':0,'tests':5,'log_sha256':'40f7e110622821adb808c0c2f2150f5e955e3d6a307e1ff3efcc46d7cbc68235','faults':'Nested condition snapshot/classical mutation, discarded phase block and budget fault; independent6-variable64-assignment truth check plus live-root collection/ID reuse'},
    'preserved_unreclaimed_graph_attempt':{'pid':2479160,'exit_code':101,'source':'decision-phase-kernel-v1.rs','kernel_sha256':'b7327efe25d9500475bf9b26a14569942b2b758de4c82579f0f81b28f259eec0','log_sha256':'c04ff9626dda6465751b2c20bdb5a320067ec9c29ff5587f5942d47a778b5f72','result':'Three fixtures exceed1million cumulative nodes; inconclusive, no phase defect diagnosed'},
    'memory_argument':'Collection marks all current quantum/classical values, phase, current predicate and predicate stack; clears operation memo and removes only unreachable unique/terminal nodes. Stable IDs of live roots are retained; dead IDs may be reused. Node and recursion budgets fail inconclusively.',
    'results':receipts}
(HERE/'decision-phase-proof-receipt.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({name:{'selected_tests':r['selected_tests'],'exact_proof_instances':len(r['proof_instances'])}for name,r in receipts.items()},indent=2))
