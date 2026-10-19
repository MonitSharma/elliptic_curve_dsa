#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-and-target-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-and-target-20261019/combo.exit' EXIT
while [ ! -f control.exit ]; do sleep 15; done
test "$(cat control.exit)" = 0
python3 preflight.py > combo-preflight.json
python3 prepare_combo.py
sha256sum combo_scan.rs combo_peak.rs detector.rs cover.py combo_cover.py Cargo.toml run-combo.sh > COMBO_SOURCE.sha256
ulimit -v 33554432
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=stable
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/product-order-20261019/target
cargo test --release --offline --bin and_combo_scan --bin and_combo_peak > combo-tests.log 2>&1
cargo build --release --offline --bin and_combo_scan --bin and_combo_peak > combo-build.log 2>&1
sha256sum "$CARGO_TARGET_DIR/release/and_combo_scan" "$CARGO_TARGET_DIR/release/and_combo_peak" > COMBO_BINARY.sha256
/usr/bin/time -v "$CARGO_TARGET_DIR/release/and_combo_scan" absorbed.ops.bin combo-scan.json > combo-scan.log 2>&1
export CARRY_SCAN="$r/combo-scan.json"
/usr/bin/time -v "$CARGO_TARGET_DIR/release/and_combo_peak" absorbed.ops.bin combo-profile > combo-profile.log 2>&1
python3 combo_cover.py > combo-cover-summary.json
