#!/usr/bin/env bash
set -euo pipefail
evidence=/home/hclau/ecdsa_research/overnight-20261014/product-evidence/classical-xor-factors
mkdir -p "$evidence"
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"' EXIT
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=1.93.0
ulimit -v 16777216
. /home/hclau/.cargo/env
date -u
python3 /home/hclau/ecdsa_research/overnight-20261014/create-xor-factors-analysis.py /home/hclau/ecdsa_research/product /home/hclau/ecdsa_research/overnight-20261014/product/src/point_add /home/hclau/ecdsa_research/overnight-20261014/product-xor-factors-analysis
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/overnight-20261014/product-anf-analysis/target
cd /home/hclau/ecdsa_research/overnight-20261014/product-xor-factors-analysis
sha256sum src/main.rs Cargo.toml ../product/src/point_add/classical_factors_xor.rs ../product/src/point_add/tests_classical_factors.rs > "$evidence/source.sha256"
/usr/bin/time -v cargo test --offline --release -- --nocapture
/usr/bin/time -v cargo build --offline --release
/usr/bin/time -v $CARGO_TARGET_DIR/release/product_anf_analysis /home/hclau/ecdsa_research/product/ops.bin "$evidence/ops.bin"
test ! -e "$evidence/ops.bin" || sha256sum "$evidence/ops.bin" > "$evidence/ops.sha256"
date -u
