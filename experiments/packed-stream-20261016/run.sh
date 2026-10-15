#!/bin/bash
set -euo pipefail
root=/home/hclau/ecdsa_research/packed-stream-20261016
cd "$root"
trap 'echo $? > /home/hclau/ecdsa_research/packed-stream-20261016/run.exit' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 RAYON_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 33554432
python3 prepare.py > prepare.log 2>&1
cd tool
cargo build --release --locked --offline > ../build.log 2>&1
cd "$root"
ops=/home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin
model=/home/hclau/ecdsa_research/prefilter-20261015/model-source
PACKED_ZERO_SHADOW=1 ./tool/target/release/value_prefilter "$ops" 1 128 2 shadow128.jsonl "$model" 128 > shadow128.log 2> shadow128.err
./tool/target/release/value_prefilter "$ops" 1 1024 2 timing-t2.jsonl "$model" 1024 > timing-t2.log 2> timing-t2.err
./tool/target/release/value_prefilter "$ops" 1 1024 16 timing-t16.jsonl "$model" 1024 > timing-t16.log 2> timing-t16.err
PACKED_ZERO_SHADOW=1 ./tool/target/release/value_prefilter "$ops" 17 11 3 partial.jsonl "$model" 9 > partial.log 2> partial.err
sha256sum tool/target/release/value_prefilter > frozen.sha256
python3 analyze.py > analysis.log
