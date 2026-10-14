"""Prepare the fourth research checkpoint without touching submissions."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CYCLE = ROOT / 'experiments/overnight-20261014'
p = CYCLE / 'cycle.json'
data = json.loads(p.read_text(encoding='utf-8'))
data['fourth_checkpoint'] = {
    'checkpoint_prepared_utc': '2026-10-14T15:09:00Z',
    'public_refresh_utc': '2026-10-14T14:41:00Z',
    'public_records': 1562, 'eligible_records': 1221, 'pareto_points': 45,
    'records_changed': False, 'original_qualified_candidates': [],
    'N275_v2': {'generated_ops': 3832705108, 'referenced_qubits': 692,
                'stream_sha256': 'ad1205994a3927ba76e90a086eadcf800d5876efe36425495cc8e83e21c6a26f',
                'status': 'Unchanged official9024benchmark active; no qualified score',
                'nonce_target': 34, 'nonce_control': 5},
    'exact_phase': {'Q693_instances': 74, 'N275_v2_instances': 116,
                    'kernel_tests': 5, 'scope': 'All independent measurement outcomes on fixed input lanes; component evidence'},
    'constructor': '1953 mixed and2604 reverse interfaces closed without witness; H45 native/all-MR pass but actual complete guard zero; expanded builder assertion failure preserved',
    'square': 'Uniform+2 exact production-sized components pass; coupled zero-x repaired, minus2A y and phase errors persist; complete builder assertion failure and worse partial resources'
}
data['jobs_at_fourth_checkpoint'] = [{
    'pid': 2532160, 'native_evaluator_pid': 2534382,
    'kind': 'Unchanged protected official N275-v2 complete9024benchmark',
    'log': '/home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/n275-v2-official-eval.log',
    'exit': '/home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/n275-v2-official-eval.exit',
    'cycle_log': '/home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/n275-v2-official-cycle.log',
    'memory_limit_GiB': 256, 'runtime_threads': 1, 'qualified_score': None
}]
p.write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')

# Include completed evidence only. Agents keep active follow-up names separate.
paths = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard'], cwd=ROOT, text=True).splitlines()
paths += subprocess.check_output(['git', 'diff', '--name-only'], cwd=ROOT, text=True).splitlines()
excluded = ('headflag', 'actual-lean-direct-v3', 'actual_lean_direct_v3', 'native-direct-v3', '57bit', 'mw57')
selected = sorted({s for s in paths if (s.startswith('experiments/overnight-20261014/') or s.startswith('scripts/') or s in ('docs/data/latest-leaderboard.json', 'docs/frontier-results.md', 'docs/overnight-20261014.md')) and not any(x in s for x in excluded)})
for s in selected:
    file = ROOT / s
    if not file.is_file():
        raise RuntimeError(s)
    if file.suffix == '.json':
        json.loads(file.read_text(encoding='utf-8-sig'))
    if file.suffix == '.patch':
        text = file.read_text(encoding='utf-8', errors='replace')
        changed = re.findall(r'^diff --git a/(.*?) b/(.*?)$', text, re.M)
        assert changed, s
        assert all(a.startswith('src/point_add/') and b.startswith('src/point_add/') for a,b in changed), s
    if file.stat().st_size > 2_000_000:
        raise RuntimeError('Unexpected oversized checkpoint file: '+s)
outfile = ROOT / 'research-output/overnight-20261014/fourth-stage-paths.json'
outfile.write_text(json.dumps(selected, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'files': len(selected), 'bytes': sum((ROOT/s).stat().st_size for s in selected), 'excluded_active': [s for s in paths if any(x in s for x in excluded)], 'stage_list': str(outfile)}))
