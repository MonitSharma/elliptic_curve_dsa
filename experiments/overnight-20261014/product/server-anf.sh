#!/usr/bin/env bash
set -euo pipefail
evidence=/home/hclau/ecdsa_research/overnight-20261014/product-evidence/anf8
mkdir -p "$evidence"
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"' EXIT
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=1.93.0
ulimit -v 16777216
. /home/hclau/.cargo/env
date -u
python3 /home/hclau/ecdsa_research/overnight-20261014/product-create-anf-analysis.py /home/hclau/ecdsa_research/product /home/hclau/ecdsa_research/overnight-20261014/product/src/point_add /home/hclau/ecdsa_research/overnight-20261014/product-anf-analysis
cd /home/hclau/ecdsa_research/overnight-20261014/product-anf-analysis
sha256sum src/main.rs Cargo.toml ../product/src/point_add/bounded_anf.rs ../product/src/point_add/tests_bounded_anf.rs > "$evidence/source.sha256"
/usr/bin/time -v cargo test --offline --release -- --nocapture
/usr/bin/time -v cargo build --offline --release
/usr/bin/time -v target/release/product_anf_analysis /home/hclau/ecdsa_research/product/ops.bin "$evidence/ops.bin"
test ! -e "$evidence/ops.bin" || sha256sum "$evidence/ops.bin" > "$evidence/ops.sha256"
date -u
