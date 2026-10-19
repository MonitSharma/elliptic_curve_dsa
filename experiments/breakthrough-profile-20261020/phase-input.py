import json
from pathlib import Path
r=Path(__file__).resolve().parent
p=json.loads((r/'PHASE-PROFILE.json').read_text())
assert p['status']=='BYTE_IDENTICAL_ACCEPTED_CIRCUIT_DIAGNOSTIC_PROFILE'
(r/'phase-prepass.tsv').write_text(''.join(f"{x['phase']}\t{x['prepass_end']}\n" for x in p['phases']))
