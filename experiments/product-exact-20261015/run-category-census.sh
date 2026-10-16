#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=category-restore-census-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$root/$out/launcher.exit"' EXIT
printf '%s\n' 'Fixed4096 batches/source (262144shots), label product-deletion-restoration-20261016. Restore all74 inherited deletion rows, retaining all70 reductions and all upstream anchors/cuts. Include every batch0..4095. Component failure/cost measurement; no source selection, nonce search or scored claim.' > "$out/DECLARATION.txt"
while [ ! -f category-restore-20261016/launcher.exit ] || [ ! -f wide-compound-native.exit ]; do sleep 30; done
test "$(cat category-restore-20261016/launcher.exit)" = 0
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 41943040
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/preflight.json"
sha256sum tip/ops.bin candidate-product-restore-deletions/ops.bin > "$out/source-streams.sha256"
exe=/home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census
"$exe" tip/ops.bin product-deletion-restoration-20261016 0 4096 4 "$out/parent-census.jsonl" > "$out/parent-census.out" 2> "$out/parent-census.err" &
parent_pid=$!;echo "$parent_pid" > "$out/parent-census.pid"
"$exe" candidate-product-restore-deletions/ops.bin product-deletion-restoration-20261016 0 4096 4 "$out/candidate-census.jsonl" > "$out/candidate-census.out" 2> "$out/candidate-census.err" &
candidate_pid=$!;echo "$candidate_pid" > "$out/candidate-census.pid"
wait "$parent_pid";echo 0 > "$out/parent-census.exit"
wait "$candidate_pid";echo 0 > "$out/candidate-census.exit"
python3 summarize_category_census.py > "$out/summary.out"
