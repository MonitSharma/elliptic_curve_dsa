#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product-parent-sat-20261019
trap 'rc=$?; printf "%s\n" "$rc" > causal.exit' EXIT
date -Is > causal-started.txt
uptime > causal-resources.txt
free -g >> causal-resources.txt
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 33554432
source /home/hclau/.cargo/env
sha256sum Cargo.toml taint.rs io.rs run-causal.sh > CAUSAL-SOURCE.sha256
cargo test --release --offline --bin taint > causal-tests.log 2>&1
cargo build --release --offline --bin taint > causal-build.log 2>&1
target/release/taint /home/hclau/ecdsa_research/product-pareto-20261019/parent/ops.bin ZERO-ROW-CAUSAL.json > causal.log 2>&1
