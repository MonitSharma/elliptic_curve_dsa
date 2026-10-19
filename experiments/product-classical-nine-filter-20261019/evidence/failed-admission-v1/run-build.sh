#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-classical-nine-filter-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-classical-nine-filter-20261019/build.exit' EXIT
python3 ../autonomous-20261019/preflight_v8.py > build-preflight.json
sha256sum prepare.py run-build.sh ../autonomous-20261019/preflight_v8.py > BUILD_SOURCE.sha256
ulimit -v 33554432
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 RUSTUP_TOOLCHAIN=stable
unset CARGO_TARGET_DIR
python3 prepare.py > prepare.log 2>&1
cd "$r/tool"
cargo build --release --locked --offline --bin value_prefilter > "$r/build.log" 2>&1
sha256sum ./target/release/value_prefilter > "$r/BINARY.sha256"
