"""Set only the lowest passing identity-tail nonce on the frozen circuit."""
from pathlib import Path
import json
import re
root=Path(__file__).resolve().parent
assert json.loads((root/'evidence/paired-summary.json').read_text())['passes_failure_gate']
out=(root/'evidence/screen.out').read_text()
match=re.search(r'^SELECTED nonce=(\d+) .*nonces_screened=(\d+)$',out,re.M)
assert match, 'No passing nonce selected'
nonce, screened=map(int,match.groups())
assert re.search(r'SELECTED_OFFICIAL_REPLAY nonce='+str(nonce)+r' ok=true shots=9024 classical=0 phase_batches=0 ancilla_batches=0',out)
rows=[json.loads(l) for l in (root/'evidence/screen.jsonl').read_text().splitlines()]
by_nonce={r['nonce']:r for r in rows}
assert len(rows)==len(by_nonce)==screened
assert all(n in by_nonce and not by_nonce[n]['pass'] for n in range(1,nonce))
assert by_nonce[nonce]['pass']
p=root/'candidate/src/point_add/mod.rs'
s=p.read_text()
assert s.count('"TAIL_NONCE" => "375",')==1
p.write_text(s.replace('"TAIL_NONCE" => "375",',f'"TAIL_NONCE" => "{nonce}",'))
(root/'evidence/selection.json').write_text(json.dumps({'nonce':nonce,'screened':screened,'policy':'ascending_from_1_lowest_pass','selected_for_Toffolis':False},indent=2)+'\n')
