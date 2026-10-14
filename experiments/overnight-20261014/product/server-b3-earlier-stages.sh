#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014
checkout=$root/product-b3-earlier-stages
evidence=$root/product-evidence/b3-earlier-stages
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"; python3 "$root/research-receipt.py" "$checkout" "$evidence/receipt" --log "$evidence/run.log" --exit "$evidence/run.exit" --stream "$evidence/run/ops.bin"; exit "$rc"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 CARGO_TARGET_DIR=$root/product-b3-earlier-stages-target
date -u
hostname
cd "$checkout"
git rev-parse HEAD
git status --short
sha256sum src/point_add/mod.rs src/point_add/product_b3_stage_observer.rs > "$evidence/source.sha256"
/usr/bin/time -v env -i HOME="$HOME" PATH="$PATH" USER="$USER" CARGO_BUILD_JOBS=4 CARGO_TARGET_DIR="$CARGO_TARGET_DIR" RUSTUP_TOOLCHAIN=1.93.0 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 cargo build --offline --locked --release --bin build_circuit
sha256sum "$CARGO_TARGET_DIR/release/build_circuit" > "$evidence/native.sha256"
cd "$evidence/run"
/usr/bin/time -v env -i HOME="$HOME" PATH="$PATH" USER="$USER" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 "$CARGO_TARGET_DIR/release/build_circuit"
sha256sum ops.bin "$evidence/"*.bin > "$evidence/streams.sha256"
cmp ops.bin "$root/product-evidence/b3-baseline/run/ops.bin"
date -u
