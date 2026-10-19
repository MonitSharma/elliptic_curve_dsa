#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-factor-cost-proof-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-factor-cost-proof-20261019/run.exit' EXIT
python3 ../autonomous-20261019/preflight_v3.py > preflight.json
sha256sum cost_proof.rs guard_prefix.rs io.rs Cargo.toml run.sh ../autonomous-20261019/preflight_v3.py > SOURCE.sha256
ulimit -v 33554432
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=stable
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/product-order-20261019/target
cargo build --release --offline --bin factor_cost_proof > build.log 2>&1
sha256sum "$CARGO_TARGET_DIR/release/factor_cost_proof" > BINARY.sha256
/usr/bin/time -v "$CARGO_TARGET_DIR/release/factor_cost_proof" "$r" > proof.log 2>&1
