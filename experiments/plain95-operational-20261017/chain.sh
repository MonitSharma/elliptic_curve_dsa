#!/bin/bash
# PRODUCT95 end-to-end preparation, then the ascending nonce search (queue mode; never submits).
# Every step stops the chain on failure and keeps its logs.
set -euo pipefail
ws=/home/hclau/ecdsa_research
op=$ws/plain95-operational-20261017
cd "$op"
echo $$ > chain.pid
trap 'echo $? > '"$op"'/chain.exit' EXIT
log() { echo "$(date -Is) $*" >> "$op/chain.log"; }
cert=$ws/product-exact-20261015/cache-certificate95-20261017
log "waiting for universal95 certificate"
while [ ! -e "$cert/launcher.exit" ]; do sleep 30; done
test "$(cat $cert/launcher.exit)" = 0
grep -q UNIVERSAL95_CHAIN_PASS "$cert/chain.log"
cd $ws/product-exact-20261015
[ -e "$cert/CACHE_EQUIVALENCE_CERTIFICATE.json" ] || python3 consolidate_cache_certificate95.py > "$cert/consolidate.log" 2>&1
[ -e "$cert/PER_INPUT_MASK_TRANSFER.json" ] || python3 write_mask_transfer95.py > "$cert/mask-transfer.log" 2>&1
[ -e PRODUCT95_ABI.json ] || python3 write_abi95.py > "$cert/abi.log" 2>&1
log "certificate consolidated"
f=$ws/product95-filter-20261017
if [ ! -e "$f/run.exit" ]; then bash "$f/run.sh"; fi
test "$(cat $f/run.exit)" = 0
python3 - <<'PY'
import hashlib,json
from pathlib import Path
f=Path('/home/hclau/ecdsa_research/product95-filter-20261017')
r=json.loads((f/'RESULT.json').read_text());assert r['status']=='DISABLED_PRODUCT95_PIPELINE_QUALIFICATION_PASS'
out=f/'QUALIFIED_BASELINE.json'
if not out.exists():out.write_text(json.dumps({'baseline-0.jsonl':hashlib.sha256((f/'baseline-0.jsonl').read_bytes()).hexdigest(),'result_sha256':hashlib.sha256((f/'RESULT.json').read_bytes()).hexdigest()},indent=2)+'\n')
PY
log "filter qualified"
cd "$op"
bash prepare-all.sh
test "$(cat prepare-all.exit)" = 0
log "acceptance and control passed; launching search"
bash run-search.sh
log "search finished: $(cat search.exit)"
