#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014
evidence=$root/product-evidence/b3-stage-replay
runner=$root/product-b3-stage-replay
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"; exit "$rc"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 CARGO_TARGET_DIR=$root/product-b3-stage-replay-target
export RUSTUP_TOOLCHAIN=1.93.0 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
date -u
hostname
python3 "$evidence/prepare-b3-stage-replay.py" "$root/product-b3-baseline" "$runner" "$root/product-evidence/b3-paired"
sha256sum "$runner/src/main.rs" "$runner/Cargo.toml" "$runner/known-official-failures.tsv" "$root/product-evidence/b3-paired/independent.tsv" > "$evidence/source-packets.sha256"
cd "$runner"
/usr/bin/time -v cargo build --offline --release
sha256sum "$CARGO_TARGET_DIR/release/product_paired_diagnostic" > "$evidence/native.sha256"
sha256sum "$root/product-evidence/b3-stages/"*.bin > "$evidence/streams.sha256"
/usr/bin/time -v "$CARGO_TARGET_DIR/release/product_paired_diagnostic" "$root/product-evidence/b3-stages" "$runner/known-official-failures.tsv" "$root/product-evidence/b3-paired/independent.tsv"
date -u
