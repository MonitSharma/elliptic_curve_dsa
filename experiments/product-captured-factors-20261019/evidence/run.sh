#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-captured-factors-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-captured-factors-20261019/run.exit' EXIT
while [ ! -f ../product-classical-factors-refresh-20261019/run.exit ] || [ ! -f ../product-classical-factors-refresh-20261019/control.exit ]; do sleep 15; done
test "$(cat ../product-classical-factors-refresh-20261019/run.exit)" = 0
test "$(cat ../product-classical-factors-refresh-20261019/control.exit)" = 0
python3 preflight.py > preflight.json
sha256sum capture_only.rs io.rs Cargo.toml run.sh prepare.py factor.py preflight.py > SOURCE.sha256
ulimit -v 33554432
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=stable
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/product-order-20261019/target
cargo test --release --offline --bin capture_only > tests.log 2>&1
cargo build --release --offline --bin capture_only > build.log 2>&1
sha256sum Cargo.lock "$CARGO_TARGET_DIR/release/capture_only" > BINARY.sha256
/usr/bin/time -v "$CARGO_TARGET_DIR/release/capture_only" ../product-pareto-20261019/candidate-parent4/ops.bin captured 97c40ed1dd3f5123c9554ebf29c54c433960804c0effce63dc7bba52844ae9ae > capture.log 2>&1
/usr/bin/time -v python3 factor.py > factor.log 2>&1
