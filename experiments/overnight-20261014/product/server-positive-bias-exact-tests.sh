#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/overnight-20261014/product-positive-bias-exact
evidence=/home/hclau/ecdsa_research/overnight-20261014/product-evidence/positive-bias-exact
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/tests.exit"; python3 ../research-receipt.py . "$evidence/receipt" --log "$evidence/tests.log" --exit "$evidence/tests.exit"; exit "$rc"' EXIT
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/overnight-20261014/product-positive-bias-exact-target
ulimit -v 16777216
. /home/hclau/.cargo/env
date -u
hostname
git rev-parse HEAD
git status --short
sha256sum src/point_add/square.rs src/point_add/tests_positive_bias.rs src/point_add/tests_positive_large.rs src/point_add/tests_positive_phase_polynomial.rs > "$evidence/test-source.sha256"
/usr/bin/time -v cargo test --offline --locked --release --bin build_circuit uniform_positive_large -- --nocapture --test-threads=1
find "$CARGO_TARGET_DIR/release/deps" -maxdepth 1 -type f -name 'build_circuit-*' -executable -exec sha256sum {} \; > "$evidence/test-native.sha256"
date -u
