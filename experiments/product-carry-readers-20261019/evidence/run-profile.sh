#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-carry-readers-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-carry-readers-20261019/profile.exit' EXIT
python3 preflight.py > profile-preflight.json
sha256sum peak_profile.rs Cargo.toml run-profile.sh > PROFILE_SOURCE.sha256
ulimit -v 33554432
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=stable
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/product-order-20261019/target
cargo test --release --offline --bin carry_peak_profile > profile-tests.log 2>&1
cargo build --release --offline --bin carry_peak_profile > profile-build.log 2>&1
sha256sum "$CARGO_TARGET_DIR/release/carry_peak_profile" > PROFILE_BINARY.sha256
export CARRY_SCAN="$r/scan.json"
/usr/bin/time -v "$CARGO_TARGET_DIR/release/carry_peak_profile" ../product-pareto-20261019/parent/ops.bin profile > profile.log 2>&1
python3 verify_profile.py > profile-control.json
