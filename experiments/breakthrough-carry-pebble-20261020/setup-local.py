from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'breakthrough-phase-fusion-20261020'
(r/'launch.py').write_bytes((old/'launch.py').read_bytes())
(r/'run.sh').write_bytes((old/'run.sh').read_bytes().replace(b'breakthrough-phase-fusion-20261020',b'breakthrough-carry-pebble-20261020').replace(b'phase_fusion',b'carry_pebble'))
