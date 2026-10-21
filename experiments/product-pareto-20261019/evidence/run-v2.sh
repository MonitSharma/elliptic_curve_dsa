#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product-pareto-20261019
echo $$ > scan-v2.pid
trap 'echo $? > scan-v2.exit' EXIT
source /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 67108864
sha256sum scan.rs scan-v1.rs io.rs Cargo.toml > tool-source.sha256
cargo test --release --bin product_pareto_exact_v2 > tests-v2.log 2>&1
cargo build --release --bin product_pareto_exact_v2 > build-v2.log 2>&1
target/release/product_pareto_exact_v2 /home/hclau/ecdsa_research/product179-native-20261017/candidate/ops.bin product179-v2 512 > product179-v2.log 2>&1
while [ ! -f parent-stream.sha256 ]; do
    if [ -f discovery.exit ]; then echo 'Parent build did not complete'; exit 1; fi
    sleep 10
done
echo '99edb1d39f94c40752cb1fa2581dd2b13fe17696c486f542b8d43c1af1974683  parent/ops.bin' | sha256sum -c
target/release/product_pareto_exact_v2 parent/ops.bin parent-v2 512 > parent-v2.log 2>&1
