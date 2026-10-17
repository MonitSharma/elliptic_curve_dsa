"""Select the lowest passing nonce from the ascending exact screen and set TAIL_NONCE (only change)."""
from pathlib import Path
import hashlib, json, re
root = Path('/home/hclau/ecdsa_research/wide95-native-20261017'); e = root / 'evidence'; tree = root / 'candidate'
out = (e / 'screen.out').read_text()
m = re.search(r'^SELECTED nonce=(\d+) .*nonces_screened=(\d+)$', out, re.M); assert m, 'no pass in screened range'
nonce, screened = map(int, m.groups())
assert re.search(r'SELECTED_OFFICIAL_REPLAY nonce=' + str(nonce) + r' ok=true shots=9024 classical=0 phase_batches=0 ancilla_batches=0', out)
rows = [json.loads(x) for x in (e / 'screen.jsonl').read_text().splitlines()]; by = {r['nonce']: r for r in rows}
assert len(rows) == len(by) == screened and all(n in by and not by[n]['pass'] for n in range(1, nonce)) and by[nonce]['pass']
p = tree / 'src/point_add/mod.rs'; s = p.read_text(); old = '"TAIL_NONCE" => "375",'; assert s.count(old) == 1
p.write_text(s.replace(old, f'"TAIL_NONCE" => "{nonce}",'))
(e / 'selection.json').write_text(json.dumps({'nonce': nonce, 'screened': screened, 'policy': 'ascending_from_1_lowest_pass',
    'selected_for_Toffolis': False, 'all_lower_nonces_fail': True}, indent=2) + '\n')
print(nonce, screened)
