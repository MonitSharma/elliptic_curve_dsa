#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/simd-census-v2-20261016
echo $$ > run.pid
trap 'rc=$?; echo "$rc" > run.exit' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 33554432
python3 prepare.py
(cd tool; cargo build --release --locked --offline > ../build.log 2>&1)
exe=tool/target/release/product_paired_diagnostic
parent=/home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin
candidate=/home/hclau/ecdsa_research/product-exact-20261015/candidate-final/ops.bin
"$exe" "$parent" simd-census-validation-20261016 0 128 1 tip.jsonl 64 > tip.out 2> tip.err
cmp tip.jsonl ../simd-census-20261016/tip-reference.jsonl
"$exe" "$candidate" simd-census-validation-20261016 0 128 1 candidate.jsonl 64 > candidate.out 2> candidate.err
cmp candidate.jsonl ../simd-census-20261016/candidate-final-reference.jsonl
"$exe" "$parent" simd-census-validation-20261016 17 11 3 partial.jsonl 11 > partial.out 2> partial.err
cmp partial.jsonl ../simd-census-20261016/partial-reference.jsonl
"$exe" "$parent" simd-census-validation-20261016 0 4096 4 bench4096.jsonl 0 > bench4096.out 2> bench4096.err
cmp bench4096.jsonl ../simd-census-20261016/bench4096.jsonl
