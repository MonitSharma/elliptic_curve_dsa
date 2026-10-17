"""Wait for the account's sole validation slot, then upload approved WIDE95."""
import json
from pathlib import Path
import subprocess
import time
from datetime import datetime, timezone
from urllib.request import urlopen

root = Path('/home/hclau/ecdsa_research/submission-approved-20261017')
plain = root / 'PLAIN67'
wide = root / 'WIDE95'
api = 'https://api.ecdsa.fail/api/submissions/'
sid = json.loads((plain / 'submission-response.json').read_text())['submission']['id']
deadline = time.monotonic() + 6 * 3600
last = None
while time.monotonic() < deadline:
    try:
        with urlopen(api + sid, timeout=30) as response:
            result = json.load(response)
        (plain / 'submission-status.json').write_text(json.dumps(result, indent=2) + '\n')
        status = result['submission']['status']
        if status != last:
            print(datetime.now(timezone.utc).isoformat(), sid, status, flush=True)
            last = status
        if status in ('accepted', 'rejected', 'failed', 'cancelled', 'canceled'):
            break
    except Exception as exc:
        print(type(exc).__name__, str(exc), flush=True)
    time.sleep(45)
else:
    raise SystemExit('Timed out waiting for submission slot; no retry performed')

# The previous response was a definite pre-creation account-limit conflict.
# Preserve it intact before the sole authorized retry, after the slot opens.
err = (wide / 'submission-submit.err').read_text()
assert 'account already has 1 submission(s) in flight' in err
assert (wide / 'upload.exit').read_text().strip() == '1'
assert (wide / 'submission-response.json').stat().st_size == 0
attempt = wide / 'attempt1-slot-conflict'
attempt.mkdir()
for name in ('PREUPLOAD-AUDIT.json', 'UPLOAD-STARTED.json', 'submission-response.json',
             'submission-submit.err', 'upload.exit'):
    (wide / name).rename(attempt / name)
done = subprocess.run(['python3', str(root / 'submit.py'), 'WIDE95', '--submit'])
(root / 'finish-wide95.exit').write_text(str(done.returncode) + '\n')
raise SystemExit(done.returncode)
