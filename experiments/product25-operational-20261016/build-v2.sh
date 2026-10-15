#!/bin/bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product25-operational-20261016
cd "$root"
echo $$ > build-v2.pid
trap 'echo $? > /home/hclau/ecdsa_research/product25-operational-20261016/build.exit' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > build-v2-preflight.json
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 RAYON_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 12582912
python3 prepare.py > prepare-v2.log 2>&1
cd tool
cargo test --release --locked --offline --bin value_prefilter search_order_tests -- --test-threads=1 > ../order-v2-tests.log 2>&1
cargo build --release --locked --offline > ../build-v2.log 2>&1
