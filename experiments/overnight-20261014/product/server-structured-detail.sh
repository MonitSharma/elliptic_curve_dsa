#!/usr/bin/env bash
set -euo pipefail
evidence=/home/hclau/ecdsa_research/overnight-20261014/product-evidence/structured-detail
mkdir -p "$evidence"
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"' EXIT
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/overnight-20261014/product-replay/target
ulimit -v 16777216
. /home/hclau/.cargo/env
cd /home/hclau/ecdsa_research/overnight-20261014/product-replay-detailed
sha256sum src/main.rs Cargo.toml > "$evidence/source.sha256"
/usr/bin/time -v cargo build --offline --release
/usr/bin/time -v "$CARGO_TARGET_DIR/release/product_paired_diagnostic" /home/hclau/ecdsa_research/product/ops.bin /home/hclau/ecdsa_research/overnight-20261014/product-evidence/relations7/ops.bin structured "$evidence/structured.tsv"
