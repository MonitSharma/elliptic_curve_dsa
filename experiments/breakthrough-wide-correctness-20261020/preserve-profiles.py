import subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;current=(r/'PROFILE-COMPARISON.json').read_bytes();assert b'tuple:FM_PARK_HOLD'in current;assert not(r/'PROFILE-COMPARISON-v1.json').exists();(r/'PROFILE-COMPARISON-v2.json').write_bytes(current);subprocess.run(['python3',str(r/'compare-profiles.py')],check=True,stdout=subprocess.DEVNULL);(r/'PROFILE-COMPARISON-v1.json').write_bytes((r/'PROFILE-COMPARISON.json').read_bytes());(r/'PROFILE-COMPARISON.json').write_bytes(current)
