"""Compact read-only checkpoint; completed-window counters are provisional."""
import datetime,json,time
from pathlib import Path
r=Path(__file__).resolve().parent
run=json.loads((r/'run-record.json').read_text());accept=json.loads((r/'ACCEPTANCE.json').read_text())
rows=[json.loads((r/f'worker{i}-progress.json').read_text()) for i in range(4)]
count=sum(x['cumulative_worker_rows'] for x in rows)
elapsed=time.time()-datetime.datetime.fromisoformat(run['started_utc']).timestamp();rate=count/elapsed
print(json.dumps({'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_hours':elapsed/3600,
    'completed_window_rows_reported':count,'scope':'Live reported counters; complete terminal JSONL audit still required',
    'average_reported_nonces_per_second':rate,'pilot_expected_nonces':accept['expected_nonces'],
    'expected_search_hours_at_measured_average_rate':accept['expected_nonces']/rate/3600,
    'estimate_note':'Geometric waiting time is uncertain; this is a rate-based expectation, not an ETA or completion guarantee.',
    'passing_nonce_files':len(list((r/'passes').glob('pass-*.json'))),'search_exit':(r/'search.exit').read_text().strip() if (r/'search.exit').exists() else None},indent=2))
