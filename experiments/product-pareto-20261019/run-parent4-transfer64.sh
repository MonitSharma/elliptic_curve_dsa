#!/bin/bash
set -euo pipefail
ulimit -c 0
root=/home/hclau/ecdsa_research/product-pareto-20261019
cd "$root"
test ! -e "$root/parent4-transfer64.pid"
echo $$ > "$root/parent4-transfer64.pid"
trap 'echo $? > "$root/parent4-transfer64.exit"' EXIT
python3 - <<'PY'
from pathlib import Path
import hashlib,json,shutil
r=Path.cwd();old=r/'parent4-transfer';out=r/'parent4-transfer64'
available=int(next(s.split()[1] for s in Path('/proc/meminfo').read_text().splitlines() if s.startswith('MemAvailable:')))*1024
assert available>200*1024**3
assert (old/'parent4-transfer.exit').read_text().strip()=='134'
assert 'memory allocation' in (old/'verify.log').read_text()
out.mkdir(exist_ok=False)
for name,h in json.loads((old/'PROOF-SOURCE.json').read_text()).items():
    assert hashlib.sha256((old/name).read_bytes()).hexdigest()==h
    shutil.copyfile(old/name,out/name)
shutil.copyfile(old/'PROOF-SOURCE.json',out/'PROOF-SOURCE.json')
(out/'DECLARATION.json').write_text(json.dumps({'scope':'Retry the identical 8192-term proof binary with64GiB address limit; no circuit/census changes',
    'binary':str(old/'target/release/verify_parent_extension'),
    'binary_sha256':hashlib.sha256((old/'target/release/verify_parent_extension').read_bytes()).hexdigest(),
    'memory_available_before_bytes':available,'memory_limit_GiB':64,'nonce_search_enabled':False},indent=2)+'\n')
PY
ulimit -v $((64*1024*1024))
parent4-transfer/target/release/verify_parent_extension \
  /home/hclau/ecdsa_research/product-exact-20261015/product-to67-rank-20261016/product-67-retained-1024-proxy.bin \
  parent/ops.bin parent4-transfer64/leases.json parent4-transfer64/PUBLIC-PARENT-TRANSFER.json \
  > parent4-transfer64/verify.log 2>&1
