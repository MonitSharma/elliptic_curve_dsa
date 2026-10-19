#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-carry-readers-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-carry-readers-20261019/run.exit' EXIT
python3 preflight.py > preflight.json
sha256sum scan.rs detector.rs io.rs Cargo.toml run.sh preflight.py > SOURCE.sha256
ulimit -v 33554432
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=stable
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/product-order-20261019/target
cargo test --release --offline --bin carry_read_scan > tests.log 2>&1
cargo build --release --offline --bin carry_read_scan > build.log 2>&1
sha256sum Cargo.lock "$CARGO_TARGET_DIR/release/carry_read_scan" > BINARY.sha256
/usr/bin/time -v "$CARGO_TARGET_DIR/release/carry_read_scan" ../product-pareto-20261019/parent/ops.bin scan.json > scan.log 2>&1
