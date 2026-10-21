"""Create a new immutable snapshot of small submission-qualification evidence."""
import hashlib, io, json, tarfile
from datetime import datetime, timezone
from pathlib import Path
r = Path(__file__).resolve().parent
stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
out = r / ('parent4-evidence-' + stamp + '.tar.gz')
suffixes = {'.py', '.rs', '.sh', '.json', '.jsonl', '.log', '.exit', '.pid', '.patch', '.md', '.toml', '.lock'}
paths = [p for p in r.iterdir() if p.is_file() and ('parent4' in p.name or p.name in ['NATIVE-PILOT.json', 'scan.rs', 'unwrap.rs', 'io.rs', 'test_retained_product.py'])]
for directory in r.glob('parent4-*'):
    if directory.is_dir():
        paths += [p for p in directory.rglob('*') if p.is_file() and not {'target', '.git', 'tool'}.intersection(p.relative_to(directory).parts)]
paths += [r / 'continuation84/PROGRESS.json']
data = {str(p.relative_to(r)): p.read_bytes() for p in paths if p.suffix in suffixes and p.stat().st_size < 20_000_000}
manifest = {'captured_utc': datetime.now(timezone.utc).isoformat(),
    'snapshot_not_a_completion_claim': True,
    'files': {name: hashlib.sha256(value).hexdigest() for name, value in data.items()}}
data['SNAPSHOT-MANIFEST.json'] = (json.dumps(manifest, indent=2) + '\n').encode()
with tarfile.open(out, 'x:gz') as archive:
    for name, value in data.items():
        item = tarfile.TarInfo(name)
        item.size = len(value)
        archive.addfile(item, io.BytesIO(value))
print(json.dumps({'path': str(out), 'sha256': hashlib.sha256(out.read_bytes()).hexdigest(), 'files': len(data)}))
