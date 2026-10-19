"""Save a fresh public record snapshot for breakthrough planning."""
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

out = Path(__file__).resolve().parent
snapshot = out / 'snapshots' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
snapshot.mkdir(parents=True, exist_ok=False)
url = 'https://api.ecdsa.fail/api/benchmarks/1ffb695a-309b-46b6-a728-2f97d8c7be74/submissions'
with urllib.request.urlopen(url, timeout=40) as response:
    raw = response.read()
(snapshot / 'public-submissions.json').write_bytes(raw)
rows = json.loads(raw)['submissions']
eligible = [r for r in rows if
    (r['status'] == 'accepted' or r['status'] == 'rejected' and r.get('rejectionReason') == 'score did not improve current best')
    and r.get('officialMetrics') and r.get('officialScore') == r['officialMetrics']['qubits'] * r['officialMetrics']['toffoli']]
leaders = {name: min(eligible, key=lambda r: r['officialMetrics'][key] if key else r['officialScore'])
           for name, key in [('product', None), ('qubits', 'qubits'), ('toffoli', 'toffoli')]}
for name, row in leaders.items():
    (snapshot / ('leader-' + name + '.json')).write_text(json.dumps(row, indent=2) + '\n')
summary = {'at_utc': datetime.now(timezone.utc).isoformat(), 'submissions': len(rows),
           'leaders': {name: {k: row.get(k) for k in ('id', 'officialScore', 'officialMetrics', 'submissionCommitSha')}
                       for name, row in leaders.items()}}
(snapshot / 'PUBLIC-RECORDS.json').write_text(json.dumps(summary, indent=2) + '\n')
(out / 'LATEST.json').write_text(json.dumps({'snapshot':snapshot.relative_to(out).as_posix(), 'at_utc':summary['at_utc']},indent=2)+'\n')
print(json.dumps(summary, indent=2))
