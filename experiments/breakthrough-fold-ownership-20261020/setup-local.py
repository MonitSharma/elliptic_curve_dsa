from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'breakthrough-paused-pool-audit-20261020'
(r/'launch.py').write_bytes((old/'launch.py').read_bytes())
(r/'run.sh').write_bytes((old/'run.sh').read_bytes().replace(b'breakthrough-paused-pool-audit-20261020',b'breakthrough-fold-ownership-20261020'))
