"""Reuse the completed four-stage qualification procedure for frozen wide15."""
from pathlib import Path
import json
root=Path(__file__).resolve().parent;old=root.parent/'wide-record-20261015'
for name in ['prepare.py','select.py','qualify.sh','finalize.py','receipt.py','summarize-final.py','collect.py']:
 s=(old/name).read_text()
 for a,b in [('wide-record-20261015','wide15-record-20261016'),('wide-candidate-final','candidate-wide-compound'),('wide-final.exit','wide-compound-native.exit'),('wide-final-native-tests.log','wide-compound-native-tests.log'),('21 passed; 0 failed','48 passed; 0 failed'),('WIDE_FREEZE.json','WIDE_COMPOUND_SOURCE_FREEZE.json'),('wide-four-stage-final-20261015','wide15-final-20261016'),('wide-frozen-four-stage-20261015','wide-compound-frozen-20261016'),('1464','1468')]:s=s.replace(a,b)
 if name=='prepare.py':
  s=s.replace("up/f'wide-frozen-{name}-census.jsonl'","up/f'wide-compound-frozen-20261016/{name}-census.jsonl'")
  s=s.replace("up/'candidate-wide-compound.patch'","up/'candidate-wide-compound.patch'")
  s=s.replace('predetermined four-stage','predetermined fifteen-stage')
 if name=='qualify.sh':
  s=s.replace('C=/home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census','C=/home/hclau/ecdsa_research/simd-census-20261016/bin/simd_census_v1')
  s=s.replace('"$root/evidence/final-parent-census.jsonl" >','"$root/evidence/final-parent-census.jsonl" 0 >')
  s=s.replace('"$root/evidence/final-census.jsonl" >','"$root/evidence/final-census.jsonl" 0 >')
  s=s.replace('python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/evidence/final-census-preflight.json"', '''python3 - <<'PY'
import hashlib
from pathlib import Path
p=Path('/home/hclau/ecdsa_research/simd-census-20261016/bin/simd_census_v1')
assert hashlib.sha256(p.read_bytes()).hexdigest()=='49d99d2bf380b628550c3ed979b5bf2adfc1a962fb6fd00a5df267cde853f554'
PY
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/evidence/final-census-preflight.json"''')
  s=s.replace('python3 "$root/finalize.py"','python3 "$root/finalize.py"\npython3 "$root/audit-prefix.py" > "$root/prefix-audit.log"')
  s+='\npython3 "$root/receipt.py" > "$root/receipt.log"\npython3 "$root/summarize-final.py" > "$root/final-summary.log"\n'
 if name=='collect.py':
  s=s.replace("p.suffix in ['.py','.sh','.md','.log','.exit']", "p.suffix in ['.py','.sh','.md','.log','.exit','.json','.sha256'] and p.name not in ['manifest.json','verified-manifest.json']")
 (root/name).write_text(s,newline='\n')
declaration={'candidate':'product-exact-20261015/candidate-wide-compound','frozen_stream_sha256':'9fe47b0a547b2aad68ddeb682be4f9fcab5dd184459a94f96afdc63e0e3fded8','qubits':1468,'submission_mode':'queue','nonce_policy':'ascending from1; lowest pass; never select by Toffolis','screen_limit':20000,'presearch_gate':'complete4096 paired frozen census; candidate failures <=parent and18; dirty0','final_census':{'label':'wide15-final-20261016','batches_each':16384,'shots_each':1048576,'runner_sha256':'49d99d2bf380b628550c3ed979b5bf2adfc1a962fb6fd00a5df267cde853f554','workers_each':8,'all_rows_required':True},'official_benchmark':'unchanged benchmark.sh on final source; all9024 shots and allchannels0 required','public_t_record_at_refresh_20261016_0112':753771,'source_content_changes_after_freeze':'identity-tail nonce only'}
(root/'DECLARATION.json').write_text(json.dumps(declaration,indent=2)+'\n')
