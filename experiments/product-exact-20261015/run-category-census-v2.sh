#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=category-restore-census-v2-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$root/$out/launcher.exit"' EXIT
printf '%s\n' 'Fixed4096 batches/source (262144shots), label product-deletion-restoration-20261016. Restore all74 inherited deletion rows, retaining all70 reductions and all upstream anchors/cuts. Include every batch0..4095. Component failure/cost measurement; no source selection, nonce search or scored claim.' > "$out/DECLARATION.txt"
while [ ! -f category-restore-20261016/launcher.exit ] || [ ! -f wide-compound-native.exit ]; do sleep 30; done
test "$(cat category-restore-20261016/launcher.exit)" = 101
while [ ! -f category-restore-20261016/baseline-check.exit ]; do sleep 30; done
test "$(cat category-restore-20261016/baseline-check.exit)" = 0
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 41943040
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/preflight.json"
sha256sum tip/ops.bin candidate-product-restore-deletions/ops.bin > "$out/source-streams.sha256"
exe=/home/hclau/ecdsa_research/simd-census-20261016/bin/simd_census_v1
printf '%s %s\n' 49d99d2bf380b628550c3ed979b5bf2adfc1a962fb6fd00a5df267cde853f554 "$exe" | sha256sum --check > "$out/executable-check.txt"
"$exe" tip/ops.bin product-deletion-restoration-20261016 0 4096 4 "$out/parent-census.jsonl" 0 > "$out/parent-census.out" 2> "$out/parent-census.err" &
parent_pid=$!;echo "$parent_pid" > "$out/parent-census.pid"
"$exe" candidate-product-restore-deletions/ops.bin product-deletion-restoration-20261016 0 4096 4 "$out/candidate-census.jsonl" 0 > "$out/candidate-census.out" 2> "$out/candidate-census.err" &
candidate_pid=$!;echo "$candidate_pid" > "$out/candidate-census.pid"
wait "$parent_pid";echo 0 > "$out/parent-census.exit"
wait "$candidate_pid";echo 0 > "$out/candidate-census.exit"
python3 summarize_category_census_v2.py > "$out/summary.out"
