#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=product25-frozen-census-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$out/launcher.exit"' EXIT
printf '%s\n' 'Fixed before census: original4b versus the predetermined25-stage per-donor-flag cache chain; new label product25-frozen-20261016,32768 batches2097152shots per stream,6 threads per source. Include every batch0..32767, no interim selection or stopping. Start only after native tests/bytecompare and compact11 census complete. No nonce search.' > "$out/DECLARATION.txt"
while [ ! -f product25-native.exit ]; do sleep 30; done
test "$(cat product25-native.exit)" = 0
while [ ! -f compact11-frozen-census-20261016/launcher.exit ]; do sleep 30; done
test "$(cat compact11-frozen-census-20261016/launcher.exit)" = 0
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 41943040
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/preflight.json"
python3 - <<'PY'
import hashlib,json
from pathlib import Path
r=Path.cwd();o=r/'product25-frozen-census-20261016'
plan={'label':'product25-frozen-20261016','batches_per_source':32768,'shots_per_source':2097152,'threads_per_source':6,'baseline':'tip/ops.bin','candidate':'candidate-product-final25/ops.bin','source_ops_sha256':{name:hashlib.sha256((r/name).read_bytes()).hexdigest() for name in ['tip/ops.bin','candidate-product-final25/ops.bin']},'source_freeze':'PRODUCT25_FREEZE.json','selection':'Include every batch0..32767; no interim rate selection, circuit changes or nonce search','nonce_search_performed':False,'score':None}
(o/'DECLARATION.json').write_text(json.dumps(plan,indent=2)+'\n')
PY
exe=/home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census
"$exe" tip/ops.bin product25-frozen-20261016 0 32768 6 "$out/parent-census.jsonl" > "$out/parent-census.out" 2> "$out/parent-census.err" &
parent_pid=$!;echo "$parent_pid" > "$out/parent-census.pid"
"$exe" candidate-product-final25/ops.bin product25-frozen-20261016 0 32768 6 "$out/candidate-census.jsonl" > "$out/candidate-census.out" 2> "$out/candidate-census.err" &
candidate_pid=$!;echo "$candidate_pid" > "$out/candidate-census.pid"
wait "$parent_pid";echo 0 > "$out/parent-census.exit"
wait "$candidate_pid";echo 0 > "$out/candidate-census.exit"
python3 summarize_product25_census.py > "$out/summary.out"
