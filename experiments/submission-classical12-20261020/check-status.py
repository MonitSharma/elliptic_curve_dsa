"""Fetch official status for the single recorded submission, without mutation."""
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parent
response = json.loads((root / 'submission-response.json').read_text())
sid = response['submission']['id']
with urllib.request.urlopen('https://api.ecdsa.fail/api/submissions/' + sid, timeout=60) as r:
    data = json.load(r)
stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
(root / ('status-' + stamp + '.json')).write_text(json.dumps(data, indent=2) + '\n')
(root / 'submission-status.json').write_text(json.dumps(data, indent=2) + '\n')
sub = data.get('submission', data)
keys = ('id', 'status', 'officialScore', 'officialMetrics', 'improved', 'rejectionReason',
        'submissionCommitSha', 'evaluatedCommitSha', 'evaluationId', 'promotionStatus',
        'promotionReason', 'promotionFinishedAt', 'updatedAt')
print(json.dumps({k: sub.get(k) for k in keys}, indent=2))
evaluation = sub.get('evaluation')
if evaluation:
    print(json.dumps(evaluation, indent=2)[:5000])
