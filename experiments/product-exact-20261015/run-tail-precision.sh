#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=tail-precision-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$out/launcher.exit"' EXIT
source /home/hclau/.cargo/env
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 CARGO_BUILD_JOBS=4
ulimit -v 41943040
printf '%s\n' 'Predetermined product tail precision probes: +1 all five widths at row136, and at rows135/136; unchanged138 rows, finalpark, anchors and inherited cuts. Fixed fresh label product-tail-width-20261016;4096 batches262144shots per constructible stream and original parent. Four threads per census, max12 total. No nonce search or source-anchor bypass.' > "$out/DECLARATION.txt"
valid=()
for name in one two; do
  if bash build-tail-precision.sh "$name"; then valid+=("$name"); fi
done
if [ "${#valid[@]}" -eq 0 ]; then printf '%s\n' 'No constructible variant; preserve generation failures.' > "$out/STATUS.txt"; exit 0; fi
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/census-preflight.json"
exe=/home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census
pids=()
"$exe" tip/ops.bin product-tail-width-20261016 0 4096 4 "$out/parent-census.jsonl" > "$out/parent-census.out" 2> "$out/parent-census.err" &
pids+=("$!");echo "${pids[-1]}" > "$out/parent-census.pid"
for name in "${valid[@]}"; do
  "$exe" "candidate-product-tail-$name/ops.bin" product-tail-width-20261016 0 4096 4 "$out/$name-census.jsonl" > "$out/$name-census.out" 2> "$out/$name-census.err" &
  pids+=("$!");echo "${pids[-1]}" > "$out/$name-census.pid"
done
for pid in "${pids[@]}"; do wait "$pid"; done
for name in parent "${valid[@]}"; do echo 0 > "$out/$name-census.exit"; done
