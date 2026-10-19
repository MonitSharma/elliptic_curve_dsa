#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-guard-schedule-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-guard-schedule-20261019/run.exit' EXIT
python3 preflight.py > preflight.json
sha256sum guard_schedule.rs io.rs Cargo.toml run.sh preflight.py > SOURCE.sha256
ulimit -v 33554432
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=stable
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/product-order-20261019/target
cargo test --release --offline --bin guard_schedule > tests.log 2>&1
cargo build --release --offline --bin guard_schedule > build.log 2>&1
sha256sum Cargo.lock "$CARGO_TARGET_DIR/release/guard_schedule" > BINARY.sha256
/usr/bin/time -v "$CARGO_TARGET_DIR/release/guard_schedule" ../product-pareto-20261019/parent/ops.bin scheduled ../product-order-combined-20261019/annotations.clean-events.bin > schedule.log 2>&1
/usr/bin/time -v "$CARGO_TARGET_DIR/release/tight_color" scheduled.ordered.ops.bin scheduled-tight > color.log 2>&1
