"""Resume only the identified paused post-benchmark coordinator."""
import hashlib
import json
import os
from pathlib import Path
import signal

root = Path('/home/hclau/ecdsa_research/product25-final-20261016')
assert hashlib.sha256((root / 'finalize.py').read_bytes()).hexdigest() == '059056e954e445a13e29361cab95f6506ee9729136593e6c0669307278c97ec2'
assert not (root / 'final.exit').exists()
expected = {
    628797: 'bash run-final.sh',
    642195: 'python3 /home/hclau/ecdsa_research/product25-final-20261016/finalize.py benchmark',
}
records = []
for pid, command in expected.items():
    proc = Path('/proc') / str(pid)
    actual = (proc / 'cmdline').read_bytes().replace(b'\0', b' ').decode().strip()
    assert actual == command, (pid, actual)
    assert os.getpgid(pid) == 628797
    assert (proc / 'status').read_text().split('State:')[1].strip().startswith('T')
    assert (proc / 'cwd').resolve() == root / 'candidate'
    records.append(dict(pid=pid, command=actual, pgid=os.getpgid(pid), stat=(proc / 'stat').read_text()))
receipt = root / 'VERIFY-RESUME-20261016.json'
assert not receipt.exists()
receipt.write_text(json.dumps(dict(authorization='User: verify the best result we have so far', processes=records), indent=2) + '\n')
os.killpg(628797, signal.SIGCONT)
print('Resumed only PRODUCT25 post-benchmark verification, PGID628797.')
