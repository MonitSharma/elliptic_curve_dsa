#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014
checkout=$root/product-b3-baseline
evidence=$root/product-evidence/b3-baseline
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"; python3 "$root/research-receipt.py" "$checkout" "$evidence/receipt" --log "$evidence/run.log" --exit "$evidence/run.exit" --stream "$evidence/run/ops.bin"; exit "$rc"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 CARGO_TARGET_DIR=$root/product-b3-baseline-target
date -u
hostname
cd "$checkout"
git rev-parse HEAD
git status --short
/usr/bin/time -v env -i HOME="$HOME" PATH="$PATH" USER="$USER" CARGO_BUILD_JOBS=4 CARGO_TARGET_DIR="$CARGO_TARGET_DIR" RUSTUP_TOOLCHAIN=1.93.0 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 cargo build --offline --locked --release --bin build_circuit
sha256sum "$CARGO_TARGET_DIR/release/build_circuit" > "$evidence/native.sha256"
cd "$evidence/run"
/usr/bin/time -v env -i HOME="$HOME" PATH="$PATH" USER="$USER" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 "$CARGO_TARGET_DIR/release/build_circuit"
sha256sum ops.bin > "$evidence/stream.sha256"
date -u
