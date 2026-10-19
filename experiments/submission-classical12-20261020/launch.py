"""Start the one-shot uploader detached, recording its process ID."""
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parent
assert not (root / 'UPLOAD-STARTED.json').exists()
assert not (root / 'upload.pid').exists()
with (root / 'launcher.log').open('xb') as log:
    proc = subprocess.Popen(['nohup', 'bash', str(root / 'run-upload.sh')],
        stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
        cwd=root, start_new_session=True)
(root / 'upload.pid').write_text(str(proc.pid) + '\n')
print(proc.pid)
