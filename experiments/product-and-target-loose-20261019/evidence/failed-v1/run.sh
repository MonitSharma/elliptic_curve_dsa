#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-and-target-loose-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-and-target-loose-20261019/run.exit' EXIT
python3 preflight.py > preflight.json
sha256sum and_target.rs subsequence_trace.rs io.rs Cargo.toml run.sh preflight.py > SOURCE.sha256
ulimit -v 33554432
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=stable
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/product-order-20261019/target
cargo test --release --offline --bin and_target_loose --bin and_target_loose_control > tests.log 2>&1
cargo build --release --offline --bin and_target_loose --bin and_target_loose_control > build.log 2>&1
sha256sum Cargo.lock "$CARGO_TARGET_DIR/release/and_target_loose" "$CARGO_TARGET_DIR/release/and_target_loose_control" > BINARY.sha256
/usr/bin/time -v "$CARGO_TARGET_DIR/release/and_target_loose" ../product-pareto-20261019/parent/ops.bin absorbed > scan.log 2>&1
/usr/bin/time -v "$CARGO_TARGET_DIR/release/tight_color" absorbed.ops.bin absorbed-tight > color.log 2>&1
/usr/bin/time -v "$CARGO_TARGET_DIR/release/and_target_loose_control" ../product-pareto-20261019/parent/ops.bin absorbed.ops.bin absorbed-tight.ops.bin absorbed.rng-map.bin absorbed.json control.json > control.log 2>&1
