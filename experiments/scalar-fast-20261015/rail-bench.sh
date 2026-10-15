#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/scalar-fast-20261015
echo $$ > rail-bench.pid
trap 'rc=$?; echo "$rc" > rail-bench.exit' EXIT
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
cp rail-tool/src/walk_native.rs optimized-walk-native.rs
MODEL=/home/hclau/ecdsa_research/prefilter-20261015/model-source
INPUT=/home/hclau/ecdsa_research/prefilter-20261015/evidence/census-coordinates4096.tsv
rail-tool/target/release/value_prefilter "$MODEL" "$INPUT" rail-optimized-predictions.jsonl > rail-optimized-timing.json
cp original-walk-native.rs rail-tool/src/walk_native.rs
(cd rail-tool; cargo build --release --locked --offline > ../rail-original-build.log 2>&1)
rail-tool/target/release/value_prefilter "$MODEL" "$INPUT" rail-original-predictions.jsonl > rail-original-timing.json
cmp rail-original-predictions.jsonl rail-optimized-predictions.jsonl
sha256sum rail-*-predictions.jsonl original-walk-native.rs optimized-walk-native.rs > rail-comparison.sha256
cat rail-optimized-timing.json rail-original-timing.json
