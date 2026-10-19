#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-and-target-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-and-target-20261019/control.exit' EXIT
test "$(cat run.exit)" = 0
python3 preflight.py > control-preflight.json
sha256sum subsequence_trace.rs Cargo.toml run-control.sh > CONTROL_SOURCE.sha256
ulimit -v 33554432
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=stable
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/product-order-20261019/target
cargo test --release --offline --bin and_target_control > control-tests.log 2>&1
cargo build --release --offline --bin and_target_control > control-build.log 2>&1
sha256sum "$CARGO_TARGET_DIR/release/and_target_control" > CONTROL_BINARY.sha256
/usr/bin/time -v "$CARGO_TARGET_DIR/release/and_target_control" ../product-pareto-20261019/parent/ops.bin absorbed.ops.bin absorbed-tight.ops.bin absorbed.rng-map.bin absorbed.json control.json > control.log 2>&1
