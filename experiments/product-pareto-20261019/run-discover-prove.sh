#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product-pareto-20261019
echo $$ > discover-prove.pid
trap 'echo $? > discover-prove.exit' EXIT
source /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 67108864
sha256sum discover.rs io.rs Cargo.toml > discover-prove-source.sha256
cargo test --release --bin product_pareto_discover > tests-discover-prove.log 2>&1
cargo build --release --bin product_pareto_discover > build-discover-prove.log 2>&1
test "$(cat unwrap-parent.exit)" = 0
target/release/product_pareto_discover parent-unwrapped.ops.bin parent-proven > parent-proven.log 2>&1
while [ ! -f unwrap.exit ]; do sleep 10; done
test "$(cat unwrap.exit)" = 0
target/release/product_pareto_discover product179-unwrapped.ops.bin product179-proven > product179-proven.log 2>&1
