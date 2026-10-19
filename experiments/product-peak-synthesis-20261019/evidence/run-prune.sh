#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product-peak-synthesis-20261019
trap 'rc=$?; printf "%s\n" "$rc" > prune.exit' EXIT
date -Is > prune-started.txt
uptime > prune-resources.txt
free -g >> prune-resources.txt
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 67108864
source /home/hclau/.cargo/env
sha256sum Cargo.toml dynamic_color.rs io.rs run-prune.sh > PRUNE-SOURCE.sha256
cargo test --release --offline --bin dynamic_color > prune-tests.log 2>&1
cargo build --release --offline --bin dynamic_color > prune-build.log 2>&1
target/release/dynamic_color /home/hclau/ecdsa_research/product-pareto-20261019/parent/ops.bin zero-events.json zero-pruned > zero-pruned.log 2>&1
