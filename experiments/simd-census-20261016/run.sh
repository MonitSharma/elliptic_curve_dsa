#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/simd-census-20261016
echo $$ > run.pid
trap 'rc=$?; echo "$rc" > run.exit' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 33554432
python3 prepare.py
(cd tool; cargo build --release --locked --offline > ../build.log 2>&1)
up=/home/hclau/ecdsa_research/product-exact-20261015
for pair in tip candidate-final; do
 tool/target/release/product_paired_diagnostic "$up/$pair/ops.bin" simd-census-validation-20261016 0 128 1 "$pair.jsonl" 64 > "$pair.out" 2> "$pair.err"
 /home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census "$up/$pair/ops.bin" simd-census-validation-20261016 0 128 4 "$pair-reference.jsonl" > "$pair-reference.out" 2> "$pair-reference.err"
 cmp "$pair.jsonl" "$pair-reference.jsonl"
done
