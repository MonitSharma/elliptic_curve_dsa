"""Freeze native actual-lean evidence, including failed fixture versions."""
import argparse
import hashlib
import json
from pathlib import Path
import re

root = Path(__file__).resolve().parents[3]
here = Path(__file__).parent
parser = argparse.ArgumentParser()
parser.add_argument('version', choices=['v3', 'v3r1', 'v3r2', 'v3r3'])
args = parser.parse_args()
evidence = root / f'research-output/overnight-20261014/toffoli/actual-lean-{args.version}'
native = json.loads((evidence / 'receipt/receipt.json').read_bytes())
log = (evidence / 'run.log').read_text()
exit_code = int((evidence / 'run.exit').read_text())
rows = []
for match in re.finditer(r'TOFFOLI_ACTUAL_LEAN_COMPONENT room=(\d+) new=(false|true) emitted=(\d+) executed=(\d+) cases=(\d+) peak=(\d+) hits=(\d+) c6_mr=(\d+)', log):
    room, new, *values = match.groups()
    rows.append(dict(room=int(room), new=new == 'true', **dict(zip(
        ['emitted', 'executed', 'cases', 'peak', 'hits', 'c6_mr'], map(int, values)))))
callers = []
for match in re.finditer(r'TOFFOLI_ACTUAL_LEAN_CALLER cap=(\d+) room=(\d+) tick=(\d+) new=(false|true) hits=(\d+) peak=(\d+) emitted=(\d+) source_caller_resource_only=true', log):
    cap, room, tick, new, hits, peak, emitted = match.groups()
    callers.append(dict(cap=int(cap), room=int(room), tick=int(tick), new=new == 'true',
                        hits=int(hits), peak=int(peak), emitted=int(emitted)))
complete = re.search(r'TOFFOLI_ACTUAL_LEAN_ALLMR exact_input_cases=(\d+) native_cases=(\d+) max_phase_terms=(\d+) max_quantum_terms=(\d+)', log)
if args.version == 'v3':
    assert exit_code == 101 and len(rows) == 2 and not complete
    assert 'left: 0' in log and 'right: 1' in log
    status = 'failed_fixture_used_analyze_ops_register_count_as_emitted_CCX'
    emitted_valid = False
elif args.version == 'v3r2':
    assert exit_code == 101 and '6 passed; 1 failed' in log and len(rows) == 4 and complete
    status = 'failed_caller_recipe_fin1_not_fin3_component_dropparameter_merged_no_actual_drops'
    emitted_valid = True
else:
    assert exit_code == 0 and '7 passed; 0 failed' in log and len(rows) == (2 if args.version == 'v3r3' else 4) and complete
    for old, new in zip(rows[::2], rows[1::2]):
        assert old['room'] == new['room'] and not old['new'] and new['new']
        assert old['emitted'] == new['emitted'] + 1
        assert old['executed'] == new['executed'] + old['cases'] // 2
    status = 'native_actual_fin3_drop1_cleanup_passed_component_only' if args.version == 'v3r3' else 'native_actual_fin3_drop0_cleanup_passed_component_only'
    emitted_valid = True
if args.version == 'v3r2':
    assert len(callers) == 1 and callers[0]['hits'] == 0
else:
    assert len(callers) == 2 and callers[0]['hits'] == 0 and callers[1]['hits'] == 1
assert all(row['peak'] <= row['cap'] for row in callers)
patch = (evidence / 'receipt/candidate.patch').read_bytes()
assert hashlib.sha256(patch).hexdigest() == native['candidate_patch_sha256']
(here / f'actual-lean-native-{args.version}.patch').write_bytes(patch)
record = {
    'status': status, 'exit': exit_code, 'pid': int((evidence / 'run.pid').read_text()),
    'baseline_revision': native['baseline_revision'], 'source_sha256': native['source_sha256'],
    'patch_sha256': native['candidate_patch_sha256'],
    'protected_tracked_changes': native['protected_tracked_changes'],
    'component_rows': rows, 'emitted_CCX_counts_valid': emitted_valid,
    'allMR_complete': dict(zip(['fixed_input_layout_cases', 'native_cases', 'maximum_phase_terms',
                               'maximum_quantum_terms'], map(int, complete.groups()))) if complete else None,
    'source_callers_resource_only': callers,
    'caller_tick_log_valid': args.version != 'v3r2',
    'actual_dropped_chunk_prefix_verified': args.version == 'v3r3',
    'fault_control_passed': 'toffoli_actual_lean_phase_fault_v3 ... ok' in log,
    'hashes': {name: hashlib.sha256((evidence / name).read_bytes()).hexdigest()
               for name in ['run.log', 'settings.txt', 'receipt/receipt.json', 'test-binary.sha256']
               if (evidence / name).exists()},
    'scope': ('loan && fin3 && ttm && lean_m && drop1; component room3 asserts one actually dropped chunk; truecaller tick129/room39. ESh absent; source mode defaults false' if args.version == 'v3r3' else 'loan && fin3 && ttm && lean_m && drop0; ESh absent; source mode defaults false') if args.version != 'v3r2' else 'Drop parameter1 but component rooms4/5 selected mergedplan with no actual dropped chunks. Caller source tick129/room40 actuallyfin1, while log tick incorrectly hardcoded128. Correct actualfin3 caller room39 and component room3 remainpending.',
    'domain': 'All16384 low/control inputs, four higher payload words, two tight-room layouts, dirty quantum passengers and512 classicalABI bits, all independent measurement outcomes via frozen fixed-input phase kernel. Arbitrary incoming phase checked natively.',
    'limits': 'Source caller proves guard/ownership/peak only, not full producer arithmetic or phase. Fin4 ESh changes E0/E1 and is unadmitted. No whole-circuit resource or score claim.',
    'qualified_score': None,
}
(here / f'actual-lean-native-{args.version}-receipt.json').write_bytes((json.dumps(record, indent=2) + '\n').encode())
print(json.dumps({'status': status, 'allMR_complete': record['allMR_complete'], 'patch_sha256': record['patch_sha256']}))
