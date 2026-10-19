#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product-peak-synthesis-20261019
trap 'rc=$?; printf "%s\n" "$rc" > zero.exit' EXIT
date -Is > zero-started.txt
uptime > zero-resources.txt
free -g >> zero-resources.txt
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 67108864
source /home/hclau/.cargo/env
sha256sum Cargo.toml zero.rs dynamic_color.rs io.rs run-zero.sh > ZERO-SOURCE.sha256
cargo test --release --offline --bin zero --bin dynamic_color > zero-tests.log 2>&1
cargo build --release --offline --bin zero --bin dynamic_color > zero-build.log 2>&1
p=/home/hclau/ecdsa_research/product-pareto-20261019/parent/ops.bin
target/release/dynamic_color "$p" none reset-recolor > reset-recolor.log 2>&1
target/release/zero "$p" zero-events 1024 > zero-events.log 2>&1
target/release/dynamic_color "$p" zero-events.json zero-recolor > zero-recolor.log 2>&1
sha256sum zero-recolor.ops.bin reset-recolor.ops.bin > ZERO-STREAMS.sha256
