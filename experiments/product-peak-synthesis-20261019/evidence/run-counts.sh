#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product-peak-synthesis-20261019
trap 'rc=$?; printf "%s\n" "$rc" > counts.exit' EXIT
uptime > counts-resources.txt
free -g >> counts-resources.txt
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 67108864
source /home/hclau/.cargo/env
sha256sum Cargo.toml dynamic_color.rs io.rs run-counts.sh > COUNTS-SOURCE.sha256
cargo test --release --offline --bin dynamic_color > counts-tests.log 2>&1
cargo build --release --offline --bin dynamic_color > counts-build.log 2>&1
target/release/dynamic_color /home/hclau/ecdsa_research/product-pareto-20261019/parent/ops.bin zero-events.json counted-prune > counted-prune.log 2>&1
