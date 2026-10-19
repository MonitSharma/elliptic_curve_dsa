#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product-schedule-20261019
trap 'rc=$?; printf "%s\n" "$rc" > commute.exit' EXIT
uptime > commute-resources.txt
free -g >> commute-resources.txt
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 67108864
source /home/hclau/.cargo/env
sha256sum Cargo.toml commute.rs io.rs run-commute.sh > COMMUTE-SOURCE.sha256
cargo test --release --offline --bin commute > commute-tests.log 2>&1
cargo build --release --offline --bin commute > commute-build.log 2>&1
target/release/commute /home/hclau/ecdsa_research/product-pareto-20261019/parent/ops.bin commute-parent > commute-parent.log 2>&1
sha256sum commute-parent.ops.bin > COMMUTE-STREAM.sha256
