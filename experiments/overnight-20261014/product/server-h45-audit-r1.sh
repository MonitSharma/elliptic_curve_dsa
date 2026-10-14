#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/overnight-20261014/product-h45-audit
evidence=/home/hclau/ecdsa_research/overnight-20261014/product-evidence/h45-audit-r1
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"; python3 ../research-receipt.py . "$evidence/receipt" --log "$evidence/run.log" --exit "$evidence/run.exit"; exit "$rc"' EXIT
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/overnight-20261014/product-h45-audit-r1-target
ulimit -v 16777216
. /home/hclau/.cargo/env
date -u
hostname
git rev-parse HEAD
git status --short
sha256sum src/point_add/y15_onefold.rs src/point_add/toffoli_carry_cleanup_v1.rs src/point_add/product_h45_phase_tests.rs src/point_add/product_h45_phase_kernel.rs > "$evidence/source.sha256"
/usr/bin/time -v cargo test --offline --locked --release --bin build_circuit product_h45_ -- --nocapture --test-threads=1
find "$CARGO_TARGET_DIR/release/deps" -maxdepth 1 -type f -name 'build_circuit-*' -executable -exec sha256sum {} \; > "$evidence/native.sha256"
date -u
