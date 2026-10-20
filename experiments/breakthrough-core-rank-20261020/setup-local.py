from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'breakthrough-carry-pebble-20261020'
(r/'launch.py').write_bytes((old/'launch.py').read_bytes())
s=(old/'run.sh').read_bytes().replace(b'breakthrough-carry-pebble-20261020',b'breakthrough-core-rank-20261020').replace(b'carry_pebble --',b'core_rank_audit_tests --')
s=s.replace(b'printf \'%s\\n\' "$rc" > run.exit',b'if [ "$rc" -eq 0 ]; then python3 rank.py > rank.log 2>&1; rc=$?; fi\nprintf \'%s\\n\' "$rc" > run.exit')
(r/'run.sh').write_bytes(s)
