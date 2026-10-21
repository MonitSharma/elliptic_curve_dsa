#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product-pareto-20261019
echo $$ > unwrap.pid
trap 'echo $? > unwrap.exit' EXIT
source /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 67108864
sha256sum unwrap.rs io.rs Cargo.toml > unwrap-source.sha256
cargo test --release --bin product_pareto_unwrap > tests-unwrap.log 2>&1
cargo build --release --bin product_pareto_unwrap > build-unwrap.log 2>&1
target/release/product_pareto_unwrap /home/hclau/ecdsa_research/product179-native-20261017/candidate/ops.bin product179-unwrapped 1024 > product179-unwrapped.log 2>&1
target/release/product_pareto_exact_v3 product179-unwrapped.ops.bin product179-unwrapped-retained 1024 > product179-unwrapped-retained.log 2>&1
