#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-guard-schedule-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-guard-schedule-20261019/control.exit' EXIT
while [ ! -f run.exit ]; do sleep 15; done
test "$(cat run.exit)" = 0
python3 preflight.py > control-preflight.json
cp Cargo.toml Cargo-initial.toml
cp Cargo-control.toml Cargo.toml
sha256sum guard_trace.rs Cargo.toml run-control.sh > CONTROL_SOURCE.sha256
ulimit -v 33554432
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=stable
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/product-order-20261019/target
cargo build --release --offline --bin guard_trace > control-build.log 2>&1
sha256sum "$CARGO_TARGET_DIR/release/guard_trace" > CONTROL_BINARY.sha256
/usr/bin/time -v "$CARGO_TARGET_DIR/release/guard_trace" ../product-pareto-20261019/parent/ops.bin scheduled.converted.ops.bin scheduled.ordered.ops.bin scheduled-tight.ops.bin CONTROL.json > control.log 2>&1
