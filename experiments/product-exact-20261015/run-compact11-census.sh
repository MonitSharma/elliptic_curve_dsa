#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=compact11-frozen-census-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
wide_pid=$(cat wide-compound-native.pid)
resume_wide() {
  rc=$?
  if ps -p "$wide_pid" -o args= | grep -q '^bash build-wide-compound-candidate.sh$'; then kill -CONT "$wide_pid"; fi
  echo "$rc" > "$out/launcher.exit"
}
trap resume_wide EXIT
test "$(cat extendedflags-native.exit)" = 0
test "$(ps -p "$wide_pid" -o args=)" = 'bash build-wide-compound-candidate.sh'
kill -STOP "$wide_pid"
printf '%s\n' "$wide_pid" > "$out/temporarily-held-wide-supervisor.pid"
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 41943040
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/preflight.json"
python3 - <<'PY'
import hashlib,json
from pathlib import Path
r=Path.cwd();o=r/'compact11-frozen-census-20261016'
plan={'label':'product-compact11-frozen-20261016','batches_per_source':32768,'shots_per_source':2097152,'threads_per_source':8,'baseline':'tip/ops.bin','candidate':'candidate-product-extendedflags/ops.bin','source_ops_sha256':{name:hashlib.sha256((r/name).read_bytes()).hexdigest() for name in ['tip/ops.bin','candidate-product-extendedflags/ops.bin']},'source_freeze':'EXTENDED_FLAGS_FREEZE.json','selection':'Include every batch0..32767; no interim rate selection, circuit changes or nonce search','nonce_search_performed':False,'score':None}
(o/'DECLARATION.json').write_text(json.dumps(plan,indent=2)+'\n')
PY
exe=/home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census
"$exe" tip/ops.bin product-compact11-frozen-20261016 0 32768 8 "$out/parent-census.jsonl" > "$out/parent-census.out" 2> "$out/parent-census.err" &
parent_pid=$!;echo "$parent_pid" > "$out/parent-census.pid"
"$exe" candidate-product-extendedflags/ops.bin product-compact11-frozen-20261016 0 32768 8 "$out/candidate-census.jsonl" > "$out/candidate-census.out" 2> "$out/candidate-census.err" &
candidate_pid=$!;echo "$candidate_pid" > "$out/candidate-census.pid"
wait "$parent_pid";echo 0 > "$out/parent-census.exit"
wait "$candidate_pid";echo 0 > "$out/candidate-census.exit"
python3 summarize_compact11_census.py > "$out/summary.out"
