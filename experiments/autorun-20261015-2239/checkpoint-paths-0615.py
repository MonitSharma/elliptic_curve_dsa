"""List only this run's reviewed files; leave the other chat and submodules alone."""
from pathlib import Path
import json
r=Path(__file__).resolve().parents[2]
paths=['docs/AGENT_HANDOFF.md','docs/research-plan.md','docs/results-status.md','docs/frontier-results.md',
    'docs/data/latest-leaderboard.json','docs/data/public-plot-points.json',
    'docs/figures/frontier.png','docs/figures/frontier.svg','docs/figures/record-tradeoffs.png','docs/figures/record-tradeoffs.svg',
    'scripts/analyze-leaderboard.py','scripts/frontier_plot.py']
def add(folder,names):paths.extend(folder+'/'+name for name in names)
add('experiments/autorun-20261015-2239',['LOG.md','READY.md','verify-followup-supplements.py','verify-repaired67-checkpoint.py',
    'verify-original37.py','verify-wide2048-source.py','refresh-isolated.py','checkpoint-paths-0615.py'])
for folder in ['experiments/original37-mask-20261016','experiments/guard-snapshot-20261016','experiments/wide2048-native-20261016']:
    paths.extend(str(p.relative_to(r)).replace('\\','/') for p in (r/folder).iterdir() if p.is_file())
add('experiments/prefilter-20261015',['STATUS.md','root-followup-supplement-verification.json','evidence-a29-wholefold-supplement.tar.gz',
    'archive-a29-wholefold-evidence.py','evidence/a29-wholefold-archive-receipt.json','a29-mask-v4/RESULTS.txt'])
add('experiments/product-exact-20261015',['STATUS.md','FOLLOWUP.md','collect.py','supplement-repaired67-qualified-20261016.tar.gz',
    'supplement-repaired67-qualified-20261016.delivery.json','REPAIRED67_INCREMENTAL_VERIFIED.json','ROOT_REPAIRED67_CHECKPOINT_VERIFIED.json',
    'REPAIR67_FREEZE.json','REPAIR67_ABI.json','repair67-census-summary.json','compare_repair67_failure_lanes.py','consolidate_repair53_certificate.py',
    'repair67-native-20261016/NATIVE_RECEIPT.json','repair67-native-20261016/PER_SHOT_FAILURE_COMPARISON.json'])
for p in (r/'experiments/product-exact-20261015/repair53-universal-20261016').iterdir():
    if p.is_file():paths.append(str(p.relative_to(r)).replace('\\','/'))
add('experiments/product25-operational-20261016',['STATUS.md','checkpoint-evidence.tar.gz','checkpoint-receipt.json','ROOT_CHECKPOINT_VERIFIED.json'])
add('experiments/quantum-borrow-family-20261016',['STATUS.md','evidence.tar.gz','manifest.json','verified-manifest.json',
    'SOURCE-VALUE-THEOREM.json','ARITHMETIC-PHASE-PROOF.md','mapped-summary.json','native-verification.json','FLAG-ERASE-PREDECLARATION.json',
    'independent-transfer-review.json','global-MR-map-proof.json','classical-interface-proof.json'])
paths=sorted(set(paths));assert all((r/p).is_file() for p in paths)
assert all(not p.startswith(('agents/','experiments/wide15-record-20261016/submission-20261016')) for p in paths)
assert 'README.md' not in paths and not any((r/p).stat().st_size>=95*1024**2 for p in paths)
dest=Path(__file__).with_suffix('.json');dest.write_text(json.dumps(paths,indent=2)+'\n')
print(f'{len(paths)} reviewed owned paths; all below95MiB; foreign README/submission/submodule edits excluded')
