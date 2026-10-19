#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-support-prune-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-support-prune-20261019/run.exit' EXIT
python3 preflight.py > preflight.json
sha256sum prune.rs io.rs Cargo.toml preflight.py run.sh > SOURCE.sha256
ulimit -v 33554432
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=stable
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/product-order-20261019/target
cargo test --release --offline --bin support_prune > tests.log 2>&1
cargo build --release --offline --bin support_prune > build.log 2>&1
sha256sum Cargo.lock "$CARGO_TARGET_DIR/release/support_prune" > BINARY.sha256
/usr/bin/time -v "$CARGO_TARGET_DIR/release/support_prune" ../product-pareto-20261019/parent/ops.bin pruned > screen.log 2>&1
