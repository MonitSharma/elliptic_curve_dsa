#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-order-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-order-20261019/run.exit' EXIT
python3 preflight.py > preflight.json
sha256sum order.rs dynamic_color.rs io.rs Cargo.toml preflight.py run.sh > SOURCE.sha256
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=stable
cargo test --release --offline --bins > tests.log 2>&1
cargo build --release --offline --bins > build.log 2>&1
sha256sum Cargo.lock target/release/order target/release/dynamic_color > BINARY.sha256
/usr/bin/time -v target/release/order ../product-pareto-20261019/parent/ops.bin reordered > order.log 2>&1
/usr/bin/time -v target/release/dynamic_color reordered.ops.bin none recolored > recolor.log 2>&1
