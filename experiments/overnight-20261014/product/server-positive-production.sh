#!/usr/bin/env bash
set -euo pipefail
label=positive-production
case "$label" in unbound-base|unbound-full-cross|producer-observation|positive-production) ;; *) exit 2;; esac
cd "/home/hclau/ecdsa_research/overnight-20261014/product-positive-production"
evidence="/home/hclau/ecdsa_research/overnight-20261014/product-evidence/$label"
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"; if test -f "$evidence/ops.bin"; then python3 ../research-receipt.py . "$evidence/receipt" --log "$evidence/run.log" --exit "$evidence/run.exit" --stream "$evidence/ops.bin"; else python3 ../research-receipt.py . "$evidence/receipt" --log "$evidence/run.log" --exit "$evidence/run.exit"; fi; exit "$rc"' EXIT
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/overnight-20261014/product-positive-production-target
ulimit -v 16777216
. /home/hclau/.cargo/env
date -u
hostname
git rev-parse HEAD
git status --short
sha256sum src/point_add/builder.rs src/point_add/leapfrog.rs src/point_add/square.rs > "$evidence/source.sha256"
/usr/bin/time -v cargo build --offline --locked --release --bin build_circuit
sha256sum "$CARGO_TARGET_DIR/release/build_circuit" > "$evidence/native-builder.sha256"
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit"
cp ops.bin "$evidence/ops.bin"
sha256sum "$evidence/ops.bin" "$evidence/raw-ops.bin" > "$evidence/ops.sha256"
date -u
