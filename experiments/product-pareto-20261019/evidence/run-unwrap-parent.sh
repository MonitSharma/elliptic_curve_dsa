#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product-pareto-20261019
echo $$ > unwrap-parent.pid
trap 'echo $? > unwrap-parent.exit' EXIT
source /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 67108864
sha256sum unwrap.rs scan.rs io.rs Cargo.toml > unwrap-parent-source.sha256
cargo test --release --bin product_pareto_unwrap --bin product_pareto_exact_v3 > tests-parent-final.log 2>&1
cargo build --release --bin product_pareto_unwrap --bin product_pareto_exact_v3 > build-parent-final.log 2>&1
echo '99edb1d39f94c40752cb1fa2581dd2b13fe17696c486f542b8d43c1af1974683  parent/ops.bin' | sha256sum -c
target/release/product_pareto_unwrap parent/ops.bin parent-unwrapped 1024 > parent-unwrapped.log 2>&1
target/release/product_pareto_exact_v3 parent-unwrapped.ops.bin parent-unwrapped-retained 1024 > parent-unwrapped-retained.log 2>&1
