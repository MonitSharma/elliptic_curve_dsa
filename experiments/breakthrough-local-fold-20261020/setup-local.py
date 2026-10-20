from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'breakthrough-paused-read-20261020'
for name in['launch.py','sweep.py']:(r/name).write_bytes((old/name).read_bytes())
(r/'run.sh').write_bytes((old/'run.sh').read_bytes().replace(b'breakthrough-paused-read-20261020',b'breakthrough-local-fold-20261020'))
