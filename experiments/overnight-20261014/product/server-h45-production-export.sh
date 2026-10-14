#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014
checkout=$root/product-h45-production-export
evidence=$root/product-evidence/h45-production-export
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"; python3 "$root/research-receipt.py" "$checkout" "$evidence/receipt" --log "$evidence/run.log" --exit "$evidence/run.exit"; exit "$rc"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 CARGO_TARGET_DIR=$root/product-h45-production-export-target
export RUSTUP_TOOLCHAIN=1.93.0 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
date -u
hostname
cd "$checkout"
git rev-parse HEAD
git status --short
sha256sum src/point_add/y15_onefold.rs src/point_add/toffoli_carry_cleanup_v1.rs src/point_add/product_h45_actual_context_tests.rs src/point_add/product_h45_phase_kernel.rs > "$evidence/source.sha256"
/usr/bin/time -v cargo test --offline --locked --release --bin build_circuit product_h45_export_actual_fold_variants -- --nocapture --test-threads=1
find "$CARGO_TARGET_DIR/release/deps" -maxdepth 1 -type f -executable -name 'build_circuit-*' -exec sha256sum '{}' + > "$evidence/native.sha256"
sha256sum "$evidence/components/"*.bin > "$evidence/components.sha256"
date -u
