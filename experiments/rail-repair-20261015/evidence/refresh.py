"""Fetch dated public records into this experiment, without changing dashboards."""
from pathlib import Path
import hashlib
import importlib.util
import json
import urllib.request

root = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('frontier', root / 'analyze-leaderboard.py')
frontier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(frontier)
rawdir = root / 'research-output/public'
rawdir.mkdir(parents=True, exist_ok=True)
data, hashes = {}, {}
for name, suffix in [('submissions', '/submissions'), ('benchmark', '')]:
    with urllib.request.urlopen(frontier.API + suffix, timeout=45) as response:
        raw = response.read()
    (rawdir / (name + '.json')).write_bytes(raw)
    hashes[name] = hashlib.sha256(raw).hexdigest()
    data[name] = json.loads(raw)[name]
summary = frontier.analyze(data['submissions'], data['benchmark'])
summary['input_sha256'] = hashes
(root / 'public-frontier.json').write_text(json.dumps(summary, indent=2) + '\n')
for track, leader in summary['leaders'].items():
    record = next(s for s in data['submissions'] if s['id'] == leader['id'])
    (rawdir / ('leader-' + track + '.md')).write_text(record.get('note') or '', encoding='utf-8')
print(json.dumps({'analyzed_at': summary['analyzed_at'], 'leaders': summary['leaders'], 'targets': summary['targets']}, indent=2))
