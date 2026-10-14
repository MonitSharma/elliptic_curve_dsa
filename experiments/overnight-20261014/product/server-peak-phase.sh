#!/usr/bin/env bash
set -euo pipefail
evidence=/home/hclau/ecdsa_research/overnight-20261014/product-evidence/peak-phase
mkdir -p "$evidence"
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"' EXIT
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/overnight-20261014/product-anf-analysis/target
ulimit -v 16777216
. /home/hclau/.cargo/env
date -u
python3 /home/hclau/ecdsa_research/overnight-20261014/create-phase-counterexample.py /home/hclau/ecdsa_research/product /home/hclau/ecdsa_research/overnight-20261014/product-phase-counterexample
cd /home/hclau/ecdsa_research/overnight-20261014/product-phase-counterexample
sha256sum src/main.rs Cargo.toml /home/hclau/ecdsa_research/product/src/point_add/pscan.rs > "$evidence/phase-source.sha256"
cargo build --offline --release
"$CARGO_TARGET_DIR/release/product_phase_counterexample"
cd /home/hclau/ecdsa_research/overnight-20261014/product-peak-analysis
sha256sum src/main.rs Cargo.toml ../product/src/point_add/bounded_anf_peak.rs > "$evidence/peak-source.sha256"
cargo build --offline --release
/usr/bin/time -v "$CARGO_TARGET_DIR/release/product_anf_analysis" /home/hclau/ecdsa_research/product/ops.bin "$evidence/unused.bin"
date -u
