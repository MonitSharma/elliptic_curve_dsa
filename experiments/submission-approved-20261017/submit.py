"""Audit preserved candidates and submit once through the authenticated CLI."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone

ROOT = Path('/home/hclau/ecdsa_research')
OUT = ROOT / 'submission-approved-20261017'
API = 'https://api.ecdsa.fail/api'
BENCH = '1ffb695a-309b-46b6-a728-2f97d8c7be74'
CLI = '/home/hclau/.local/bin/ecdsafail'

def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def get(url):
    with urllib.request.urlopen(url, timeout=45) as r:
        return json.load(r)

def git(tree, *args):
    return subprocess.check_output(['git', '-C', str(tree), *args])

def save(p, value):
    p.write_text(json.dumps(value, indent=2) + '\n')

def main(name, submit=False):
    plain = name == 'PLAIN67'
    assert name in ('PLAIN67', 'WIDE95')
    root = ROOT / ('plain67-final-20261016' if plain else 'wide95-native-20261017')
    tree = root / 'candidate'
    target = OUT / name
    target.mkdir(exist_ok=True)
    receipt = json.loads((root / 'BENCHMARK_RESULT.json').read_text())
    assert receipt['status'] == 'UNCHANGED_BENCHMARK_PASS'
    patch = git(tree, 'diff', '--binary', 'HEAD', '--', 'src/point_add')
    expected = ('cf417469ff0058622f6cdff03e6a4671c7d3fffdb108605aa8f7ed007aae9f52'
                if plain else receipt['patch_sha256'])
    assert hashlib.sha256(patch).hexdigest() == expected, 'Source changed since benchmark'
    paths = git(tree, 'diff', '--name-only', 'HEAD').decode().splitlines()
    assert paths and all(p.startswith('src/point_add/') for p in paths)
    extra = git(tree, 'ls-files', '--others', '--exclude-standard', '--', 'src/point_add').decode().splitlines()
    assert not extra, extra
    protected = git(tree, 'ls-files').decode().splitlines()
    protected = [p for p in protected if not p.startswith('src/point_add/')]
    for p in protected:
        assert (tree / p).read_bytes() == git(tree, 'show', 'HEAD:' + p), p
    if plain:
        frozen = json.loads((root / 'SOURCE_FREEZE.json').read_text())
        for p, h in frozen['source_files'].items():
            assert sha(tree / p) == h, p
        assert sha(root / 'benchmark.log') == receipt['benchmark_log_sha256']
        assert sha(root / 'score.json') == receipt['score_sha256']
        stream = root / 'native-selected.ops.bin'
        stream_hash = receipt['candidate_stream_sha256']
    else:
        stream = tree / 'ops.bin'
        stream_hash = receipt['final_stream_sha256']
        for p, h in json.loads((root / 'protected.json').read_text()).items():
            assert sha(tree / p) == h, p
        assert (root / 'evidence/benchmark.exit').read_text().strip() == '0'
        log = (root / 'evidence/benchmark.log').read_text()
        assert 'all 9024 shots OK' in log and '=== experiment OK ===' in log
    assert sha(stream) == stream_hash
    note = target / 'SUBMISSION-NOTE.md'
    assert 5120 <= note.stat().st_size <= 102400
    records = get(f'{API}/benchmarks/{BENCH}/submissions')['submissions']
    scored = [s for s in records if (s['status'] == 'accepted' or
              (s['status'] == 'rejected' and s.get('rejectionReason') == 'score did not improve current best'))
              and s.get('officialMetrics') and s.get('officialScore') ==
              s['officialMetrics']['qubits'] * s['officialMetrics']['toffoli']]
    leader = min(scored, key=lambda s: s['officialScore'] if plain else s['officialMetrics']['toffoli'])
    best = leader['officialScore'] if plain else leader['officialMetrics']['toffoli']
    candidate = receipt['product'] if plain else receipt['rounded_mean_toffoli']
    audit = dict(name=name, checked_at=datetime.now(timezone.utc).isoformat(),
                 base=git(tree, 'rev-parse', 'HEAD').decode().strip(), changed_paths=paths,
                 protected_files_checked=len(protected), patch_sha256=expected,
                 stream_sha256=stream_hash, note_sha256=sha(note),
                 public_record=leader, candidate=candidate, beats_record=candidate < best,
                 model='Claude Opus 5.5', harness='Claude Code')
    save(target / 'PREUPLOAD-AUDIT.json', audit)
    print(json.dumps({k:v for k,v in audit.items() if k != 'public_record'}, indent=2), flush=True)
    if not submit:
        return
    assert candidate < best, 'Candidate no longer improves targeted record'
    response_path = target / 'submission-response.json'
    assert not response_path.exists(), 'Existing upload response: inspect before any retry'
    command = [CLI, 'submit', '--note-file', str(note), '--dependencies-file',
               str(target / 'DEPENDENCIES.json'), '--model', 'Claude Opus 5.5',
               '--harness', 'Claude Code', '--claimed-score', str(receipt['product']), '--json']
    # Exclusive marker prevents an automatic duplicate upload after interruption.
    with (target / 'UPLOAD-STARTED.json').open('x') as f:
        json.dump({'started_at': datetime.now(timezone.utc).isoformat(), 'command':command}, f)
    with response_path.open('wb') as stdout, (target / 'submission-submit.err').open('wb') as stderr:
        done = subprocess.run(command, cwd=tree, stdout=stdout, stderr=stderr)
    (target / 'upload.exit').write_text(str(done.returncode) + '\n')
    print('upload_exit', done.returncode, flush=True)
    if done.returncode:
        print((target / 'submission-submit.err').read_text()[-5000:])
        raise SystemExit(done.returncode)
    result = json.loads(response_path.read_text())
    save(target / 'submission-status.json', get(f"{API}/submissions/{result['submission']['id']}"))
    print(json.dumps({'id':result['submission']['id'], 'status':result['submission']['status']}), flush=True)

if __name__ == '__main__':
    main(sys.argv[1], '--submit' in sys.argv[2:])
