"""Freeze producer-aware fin4 component and source-caller evidence."""
import hashlib
import json
from pathlib import Path
import re

root = Path(__file__).resolve().parents[3]
here = Path(__file__).parent
evidence = root / 'research-output/overnight-20261014/toffoli/actual-lean-v4'
native = json.loads((evidence / 'receipt/receipt.json').read_bytes())
log = (evidence / 'run.log').read_text()
assert int((evidence / 'run.exit').read_text()) == 0 and '7 passed; 0 failed' in log
rows = []
for match in re.finditer(r'TOFFOLI_ACTUAL_LEAN_V4 new=(false|true) emitted=(\d+) executed=(\d+) cases=(\d+) peak=(\d+) c6_mr=(\d+) actualdrops=2 freshESH=([^\n]+)', log):
    new, *values, esh = match.groups()
    rows.append(dict(new=new == 'true', **dict(zip(['emitted', 'executed', 'cases', 'peak', 'c6_mr'], map(int, values))), fresh_ESH_wire_ids=esh))
assert len(rows) == 2 and rows[0]['emitted'] == rows[1]['emitted'] + 1
assert rows[0]['executed'] == rows[1]['executed'] + rows[0]['cases'] // 2
proof = re.search(r'TOFFOLI_ACTUAL_LEAN_V4_ALLMR exact_input_cases=(\d+) native_cases=(\d+) max_phase_terms=(\d+) producer_rows=128 raw_bits=18 higher_words=4 room=2 classicalABI=512', log)
assert proof
callers = []
for match in re.finditer(r'TOFFOLI_ACTUAL_LEAN_V4_CALLER cap=(\d+) room=(\d+) tick=(\d+) new=(false|true) hits=(\d+) peak=(\d+) emitted=(\d+) source_caller_resource_only=true', log):
    cap, room, tick, new, hits, peak, emitted = match.groups()
    callers.append(dict(cap=int(cap), room=int(room), tick=int(tick), new=new == 'true', hits=int(hits), peak=int(peak), emitted=int(emitted)))
assert len(callers) == 2 and callers[0]['hits'] == 0 and callers[1]['hits'] == 1
assert callers[0]['emitted'] == callers[1]['emitted'] + 1 and all(row['peak'] == 1234 for row in callers)
patch = (evidence / 'receipt/candidate.patch').read_bytes()
assert hashlib.sha256(patch).hexdigest() == native['candidate_patch_sha256']
(here / 'actual-lean-native-v4.patch').write_bytes(patch)
record = {
    'status': 'native_actual_fin4_top1_direct_nondeep_drop2_passed_component_only',
    'baseline_revision': native['baseline_revision'], 'source_sha256': native['source_sha256'],
    'patch_sha256': native['candidate_patch_sha256'], 'pid': int((evidence / 'run.pid').read_text()),
    'exit': 0, 'protected_tracked_changes': native['protected_tracked_changes'],
    'component_costs': rows, 'actual_dropped_chunks': 2,
    'exact_allMR': dict(zip(['fixed_input_layout_proofs', 'native_cases', 'maximum_phase_terms'], map(int, proof.groups()))),
    'source_callers_resource_only': callers,
    'producer_contract_sha256': hashlib.sha256((here / 'actual-esh-contract-v4.json').read_bytes()).hexdigest(),
    'phase_fault_detected': 'toffoli_actual_lean_phase_fault_v4 ... ok' in log,
    'hashes': {name: hashlib.sha256((evidence / name).read_bytes()).hexdigest() for name in ['run.log', 'settings.txt', 'test-binary.sha256', 'receipt/receipt.json']},
    'native_scope': 'Seven independent top1/direct/nondeep ESHproducer inputs plus6lowpayload,3Nm,2shift controls (all18); fourhigherwords; room2; allq including3freshESH targets, dirtypads/512classABI and incomingphase; all independentHMR outcomes.',
    'physical_schedule_assertions': ['14 table helpers released beforeESHrestore', 'exactlythree ESH targets restored', 'all seven retained ESHproducer inputs outsidefold payload', 'all livehelper IDs disjoint from payload/E/Nm/shift', 'final activequbit count retained', 'component/sourcecaller cap assertion'],
    'limits': 'No genericfin4/deep producer transfer. OldE2missing model remains unadmitted. Source caller is allocation/guard/cost evidence only, not complete body arithmetic/phase. Finite higherwords alone are not all-input whole-fold proof. No full score.',
    'qualified_score': None,
}
(here / 'actual-lean-native-v4-receipt.json').write_bytes((json.dumps(record, indent=2) + '\n').encode())
print(json.dumps({'status': record['status'], 'exact_allMR': record['exact_allMR'], 'patch_sha256': record['patch_sha256']}))
