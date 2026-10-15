"""Replace only our queued, not-yet-launched single wide census."""
import os,signal
from pathlib import Path
root=Path(__file__).resolve().parent
pid=int((root/'wide-frozen-census.pid').read_text())
proc=Path('/proc')/str(pid)/'cmdline'
if proc.exists():
    args=proc.read_bytes().replace(b'\0',b' ').decode()
    assert str(root/'run-wide-frozen-census.sh') in args
    assert not (root/'wide-frozen-census-preflight.json').exists()
    os.kill(pid,signal.SIGTERM)
    (root/'wide-frozen-census.cancelled').write_text('Replaced before launch by a new fixed-label paired census using the coordinator thread loan.\n')
    print('Replaced own queued wide census; no active workload touched.')
