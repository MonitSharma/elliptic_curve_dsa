"""Explicit owned checkpoint; frozen archives carry nested evidence."""
from pathlib import Path
import json,subprocess
repo=Path(__file__).resolve().parents[2];paths=set()
def add(name):
    p=repo/name;assert p.is_file(),name
    assert p.stat().st_size<40*1024**2,name
    paths.add(p.relative_to(repo).as_posix())
for p in ['docs/AGENT_HANDOFF.md','docs/SERVER_HANDOFF.md','docs/research-plan.md','docs/results-status.md',
          'docs/data/latest-leaderboard.json','docs/frontier-results.md','docs/figures/frontier.png','docs/figures/frontier.svg']:
    add(p)
for p in ['LOG.md','checkpoint-paths-0815.py','verify-0815-evidence.py','verify-all70-base-addendum.py',
          'verify-prep-profile.py','verify-seed-native.py','verify-seed-stream-server.py']:
    add('experiments/autorun-20261015-2239/'+p)
for folder in ['census-control-family-20261016','census-control-review-20261016','scalar-window-audit-20261016',
               'all70-value-transfer-20261016','wide-cache-cleanup-audit-20261016','repair67-prep-profile-20261016',
               'n2-readonly-normalizers-20261016','search-cost-profile-20261016','wide15-retained4096-20261016']:
    for p in (repo/'experiments'/folder).iterdir():
        if p.is_file():add(p.relative_to(repo))
for p in (repo/'experiments/wide-cache-cleanup-audit-20261016/frozen-source').glob('*.rs'):add(p.relative_to(repo))
for p in ['checkpoint-evidence.tar.gz','checkpoint-receipt.json','ROOT_CHECKPOINT_VERIFIED.json']:
    add('experiments/product25-operational-20261016/'+p)
for p in ['native-source-freeze-v1.tar.gz','native-source-freeze-v1-receipt.json','native-source-freeze-v1-local-verification.json',
          'native-verification.json','PREDECLARATION.json','ROOT_NATIVE_REVIEW.json','ROOT_STREAM_REVIEW.json','verify-source-freeze.py']:
    add('experiments/seed-restore-20261016/'+p)
for p in ['all-add-attribution-addendum-v3.tar.gz','all-add-attribution-addendum-v3-receipt.json',
          'all-add-attribution-addendum-v3-local-verification.json','ROOT_ALL_ADD_V3_REVIEW.json']:
    add('experiments/current-value-attribution-20261016/'+p)
for p in ['all70-base-native-evidence.tar.gz','ROOT_ALL70_BASE_REVIEW.json']:
    add('experiments/product-exact-20261015/'+p)
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=repo,text=True).strip(),'Preserve foreign index'
assert all(p!='README.md' and 'submission-20261016/' not in p and 'prefilter-macro-' not in p for p in paths)
ignored=subprocess.run(['git','check-ignore','--stdin'],cwd=repo,input='\n'.join(paths)+'\n',text=True,capture_output=True)
assert not ignored.stdout.strip(),ignored.stdout
paths=sorted(paths);out=Path(__file__).with_suffix('')
out.with_suffix('.json').write_text(json.dumps(paths,indent=2)+'\n')
out.with_suffix('.nul').write_bytes(b'\0'.join(p.encode() for p in paths)+b'\0')
subprocess.run(['git','diff','--check','--',*paths],cwd=repo,check=True)
print(json.dumps(dict(owned_paths=len(paths),bytes=sum((repo/p).stat().st_size for p in paths),foreign_and_active_agent_work_excluded=True)))
