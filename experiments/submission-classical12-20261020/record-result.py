"""Add the official result while preserving unrelated working-tree edits."""
import difflib
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[2]
out = Path(__file__).resolve().parent
s = json.loads((out / 'submission-status.json').read_text())['submission']
assert s['status'] == 'accepted', s['status']
assert s['officialMetrics'] == {'qubits': 1234, 'toffoli': 761077}
assert s['officialScore'] == 939169018
assert s['improved'] is True
assert s['note'].startswith('Model: GPT-6 sol\nHarness: Codex\n')
sid = s['id']
url = 'https://api.ecdsa.fail/api/submissions/' + sid
text = f'''## Official product result · 20 October 2026

Official submission [{sid[:8]}]({url}) is **accepted** at
**1,234 qubits × 761,077 rounded mean executed Toffolis = 939,169,018**.
This improves the pre-upload public product 939,192,464 by **23,446 (0.00250%)**.
AI model: **GPT-6 sol**; coding harness: **Codex**. The official metrics match
the complete local benchmark. This supersedes the dated queued status below.

The public note includes the sole final passing census (262,144 × 64 shots
per source), nonce 7,614,812 and all 7,811,072 production nonce screens,
with repeated controls and parallel overrun disclosed. Original evidence and
failed-gate verdicts are preserved. Inherited approximate arithmetic remains.
Promotion status at this snapshot: `{s.get('promotionStatus')}`.

[Official receipt and disclosures](RECEIPT_LINK) ·
[Frozen source and benchmark](SOURCE_LINK)

'''
changes = []
for name in ('README.md', 'docs/research-plan.md', 'docs/results-status.md', 'docs/AGENT_HANDOFF.md'):
    path = root / name
    head = subprocess.check_output(['git', 'show', 'HEAD:' + name], cwd=root).decode()
    working = path.read_bytes()
    assert 'Official product result · 20 October 2026' not in working.decode('utf-8')
    prefix = '' if name == 'README.md' else '../'
    block = text.replace('RECEIPT_LINK', prefix + 'experiments/submission-classical12-20261020/STATUS.md')
    block = block.replace('SOURCE_LINK', prefix + 'experiments/classical12-final-20261020/SUBMISSION-NOTE.md')
    first, rest = head.split('\n', 1)
    updated_head = first + '\n\n' + block + rest.lstrip('\n')
    changes.extend(difflib.unified_diff(head.splitlines(keepends=True), updated_head.splitlines(keepends=True),
        fromfile='a/' + name, tofile='b/' + name))
    # Retain every byte of the original working-tree body, including CRLF.
    first_bytes, rest_bytes = working.split(b'\n', 1)
    ending = b'\r\n' if first_bytes.endswith(b'\r') else b'\n'
    addition = block.encode().replace(b'\n', ending)
    path.write_bytes(first_bytes + b'\n' + ending + addition + rest_bytes)
(out / 'documentation-index.patch').write_text(''.join(changes), encoding='utf-8', newline='\n')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
record = {'recorded_at_utc': datetime.now(timezone.utc).isoformat(), 'id': sid,
    'status': s['status'], 'officialScore': s['officialScore'], 'officialMetrics': s['officialMetrics'],
    'model': 'GPT-6 sol', 'harness': 'Codex', 'improved': s['improved'],
    'promotionStatus': s.get('promotionStatus'), 'promotionFinishedAt': s.get('promotionFinishedAt'),
    'submissionCommitSha': s.get('submissionCommitSha'), 'url': url,
    'submission_response_sha256': sha(out / 'submission-response.json'),
    'official_status_sha256': sha(out / 'submission-status.json'),
    'note_file_sha256': sha(out / 'SUBMISSION-NOTE-OFFICIAL.md'),
    'preupload_audit_sha256': sha(out / 'PREUPLOAD-AUDIT.json'),
    'uploaded_once': True, 'source_unchanged': True, 'original_queued_evidence_preserved': True}
(out / 'OFFICIAL-RESULT.json').write_text(json.dumps(record, indent=2) + '\n')
(out / 'STATUS.md').write_text(f'''# Official classical12 product submission

**Accepted**: [{sid[:8]}]({url}). Official Q1234 × T761077 = **939169018**,
improvement **23446 (0.00249640%)** over the live public parent at upload.
Official values match the complete unchanged 9024-shot local benchmark.
Model **GPT-6 sol**, harness **Codex**, as explicitly requested by the user.
Promotion status: `{s.get('promotionStatus')}`.

Uploaded once after a fresh public-record check and byte-level verification
of all 180 source files, 17 protected tracked files, patch, stream, original
benchmark log, score and final evidence archive. Source changes are confined
to src/point_add. No source/nonce/census changes were made for this upload.

The [public note](SUBMISSION-NOTE-OFFICIAL.md) contains complete statistical
and nonce disclosures, the declared direct [dependency](DEPENDENCIES.json),
and the predecessor note with inherited notices. The uploader added the
verified `Model: GPT-6 sol` / `Harness: Codex` public headers. The exact
uploaded note is retained in [submission-response.json](submission-response.json).

Original [queued evidence](../classical12-final-20261020/QUEUED-READY.json)
and its hashes remain unchanged. The [pre-upload audit](PREUPLOAD-AUDIT.json),
[upload response](submission-response.json), timestamped official status
snapshots and [result manifest](OFFICIAL-RESULT.json) preserve provenance.
The sole final gate remains PASS, label pareto-parent4-classical12-gate-20261019-v1,
262144 × 64 shots per source, b2912/c2967, exact p0.767413091467709,
value failures28574/28574, dirty0, failed batches per packet17.829391479492188.
Selected nonce7614812; 7811072 unique production screens plus separately
disclosed repeated control attempts. All earlier failures remain final.

Runner2276673 exited0; CLI upload.exit0; no uploader is left running.
No other project workloads were changed. The initial shell launch did not
start an upload; its absence of process/marker/output was checked before the
recorded detached launcher began. UPLOAD-STARTED.json prevents repeat uploads.
''', encoding='utf-8')
print(json.dumps(record, indent=2))
