#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/prefilter-20261015
trap 'echo $? > /home/hclau/ecdsa_research/prefilter-20261015/evidence/fast-screen-c.exit' EXIT
echo $$ > evidence/fast-screen-c.pid
ulimit -v 62914560
uptime > evidence/fast-screen-c.resources
free -g >> evidence/fast-screen-c.resources
export RAYON_NUM_THREADS=1
/usr/bin/time -v tool/target/release/fast_screen_c /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin 1 128 8 evidence/fast-screen-c-1-128.jsonl > evidence/fast-screen-c-1-128.out 2> evidence/fast-screen-c-1-128.err
python3 - <<'PY'
import json
from pathlib import Path
p=Path('evidence')
def read(n):return {r['nonce']:r for r in map(json.loads,(p/n).read_text().splitlines())}
a=read('fast-screen-c-1-128.jsonl');b=read('fast-screen-1-128.jsonl')
assert a.keys()==b.keys()
for n in a:
 for k in ['pass','batches_run','kind']:assert a[n][k]==b[n][k],(n,k,a[n],b[n])
r=dict(nonces=len(a),first=min(a),last=max(a),batches=sum(r['batches_run'] for r in a.values()),exact_agreement=len(a),c_thread_seconds=sum(r['secs'] for r in a.values()),rust_thread_seconds=sum(r['secs'] for r in b.values()))
(p/'fast-screen-c-differential.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r))
PY
