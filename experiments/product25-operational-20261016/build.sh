#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product25-operational-20261016
echo $$ > build.pid
trap 'echo $? > build.exit' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > build-preflight.json
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 RAYON_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 12582912
python3 prepare.py > prepare.log 2>&1
cd tool
cargo test --release --locked --offline --bin value_prefilter search_order_tests -- --test-threads=1 > ../order-tests.log 2>&1
cargo build --release --locked --offline > ../build.log 2>&1
