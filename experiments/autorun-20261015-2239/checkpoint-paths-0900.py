"""Explicit owned checkpoint; keep the other chat's README/submission/index intact."""
from pathlib import Path
import json, subprocess

repo = Path(__file__).resolve().parents[2]
paths = set()

def add(path):
    path = Path(path)
    if not path.is_absolute():
        path = repo / path
    assert path.is_file() and path.stat().st_size < 40 * 1024**2, str(path)
    paths.add(path.relative_to(repo).as_posix())

for name in ['docs/AGENT_HANDOFF.md', 'docs/SERVER_HANDOFF.md', 'docs/research-plan.md',
             'docs/results-status.md', 'docs/data/latest-leaderboard.json',
             'docs/frontier-results.md', 'docs/figures/frontier.png', 'docs/figures/frontier.svg']:
    add(name)
for name in ['LOG.md', 'checkpoint-paths-0900.py', 'verify-0830-evidence.py', 'verify-all70-program-server.py']:
    add('experiments/autorun-20261015-2239/' + name)
for folder in ['wide15-retained4096-20261016', 'all70-mask-feasibility-20261016',
               'all70-zero-mr-20261016', 'repair67-persistent-cost-20261016',
               'plain67-persistent-pilot-20261016', 'plain67-operational-proposal-20261016',
               'census-preseed-family-20261016', 'product25-terminal-independent-20261016']:
    for path in (repo / 'experiments' / folder).iterdir():
        if path.is_file():
            add(path)
for folder, names in {
    'product25-operational-20261016': ['ROOT_TERMINAL_AUDIT.json', 'run-terminal-audit.sh',
                                     'final-census.py', 'selected-source-freeze.json', 'STATUS.md'],
    'census-control-review-20261016': ['native-review-v2.tar.gz', 'ROOT_NATIVE_CONTROL_REVIEW.json'],
    'census-deletion-family-20261016': ['source-only-v1.tar.gz', 'ROOT_DELETION_INVENTORY_REVIEW.json'],
    'census-deletion-n2-join-20261016': ['source-only-v1.tar.gz', 'ROOT_DELETION_N2_JOIN_REVIEW.json'],
    'n2-temporal-storage-20261016': ['source-only-temporal-v1.tar.gz', 'ROOT_TEMPORAL_REVIEW.json'],
    'census-all74-fixed67-20261016': ['native-base-evidence-v1.tar.gz', 'native-base-evidence-v1-receipt.json',
                                    'native-base-local-verification.json', 'verify-base-archive.py'],
    'product25-final-20261016': ['finalize.py', 'run-final.sh'],
}.items():
    for name in names:
        path = repo / 'experiments' / folder / name
        # Review receipts are independently named; archives and required sources must exist.
        if name.startswith('ROOT_') and not path.exists():
            continue
        add(path)
assert not subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=repo, text=True).strip()
assert all(p != 'README.md' and 'submission-20261016/' not in p and 'prefilter-macro-' not in p for p in paths)
paths = sorted(paths)
ignored = subprocess.run(['git', 'check-ignore', '--stdin'], cwd=repo,
                         input='\n'.join(paths) + '\n', text=True, capture_output=True)
assert not ignored.stdout.strip(), ignored.stdout
out = Path(__file__).with_suffix('')
out.with_suffix('.json').write_text(json.dumps(paths, indent=2) + '\n')
out.with_suffix('.nul').write_bytes(b'\0'.join(p.encode() for p in paths) + b'\0')
subprocess.run(['git', 'diff', '--check', '--', *paths], cwd=repo, check=True)
print(json.dumps(dict(owned_paths=len(paths), bytes=sum((repo / p).stat().st_size for p in paths),
                      excludes_foreign_readme_submission_and_active_nested_trees=True)))
