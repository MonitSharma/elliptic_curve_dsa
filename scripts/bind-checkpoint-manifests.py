"""Bind completed checkpoint manifests to exact staged Git blob bytes."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CYCLE = ROOT / 'experiments/overnight-20261014'

def blob(path):
    return subprocess.check_output(['git', 'show', ':' + path], cwd=ROOT)

changed = []
for name in ('product/checkpoint-fifth-manifest.json',
             'toffoli/fifth-checkpoint-receipt.json',
             'toffoli/lazy-v6-checkpoint-receipt.json'):
    p = CYCLE / name
    d = json.loads(p.read_text(encoding='utf-8-sig'))
    for entry in d.get('files', []):
        raw = blob(entry['path'])
        entry['sha256'] = hashlib.sha256(raw).hexdigest()
        entry['bytes'] = len(raw)
        entry['hash_scope'] = 'exact_staged_git_blob'
    for field in ('new_completed_files', 'completed_files'):
        if isinstance(d.get(field), dict):
            for path in d[field]:
                d[field][path] = hashlib.sha256(blob(path)).hexdigest()
    field = 'files_expected_Git_LF_blob_sha256'
    if field in d:
        for filename in d[field]:
            path = (p.parent / filename).relative_to(ROOT).as_posix()
            d[field][filename] = hashlib.sha256(blob(path)).hexdigest()
    d['committed_hash_scope'] = ('Exact staged Git blob bytes. LF-normalized text; '
                                 'byte-preserved patches and gzip archives. Scientific '
                                 'original context/report bytes recoverable from gzip '
                                 'archives named in format/encoding provenance.')
    p.write_text(json.dumps(d, indent=2) + '\n', encoding='utf8')
    changed.append(str(p.relative_to(ROOT)))
print(json.dumps(changed))
