#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-classical-nine-proof-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-classical-nine-proof-20261019/edits.exit' EXIT
python3 ../autonomous-20261019/preflight_v7.py > edits-preflight.json
sha256sum verify_edits.rs Cargo-edits.toml run-edits.sh ../autonomous-20261019/preflight_v7.py > EDITS_SOURCE.sha256
cp Cargo.toml Cargo-initial.toml
cp Cargo-edits.toml Cargo.toml
ulimit -v 33554432
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export RUSTUP_TOOLCHAIN=stable CARGO_TARGET_DIR=/home/hclau/ecdsa_research/product-order-20261019/target
cargo build --release --offline --bin classical_nine_edits > edits-build.log 2>&1
sha256sum "$CARGO_TARGET_DIR/release/classical_nine_edits" > EDITS_BINARY.sha256
/usr/bin/time -v "$CARGO_TARGET_DIR/release/classical_nine_edits" "$r" > edits.log 2>&1
