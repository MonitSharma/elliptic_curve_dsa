#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-classical-factors-refresh-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-classical-factors-refresh-20261019/control.exit' EXIT
while [ ! -f parent4.json ]; do sleep 15; done
python3 control-preflight.py > control-preflight.json
# Both native source-screen binaries are already built; adding a separate bin
# does not modify either running binary or its source.
cp Cargo.toml Cargo-initial.toml
cp Cargo-control.toml Cargo.toml
sha256sum factor_trace.rs Cargo.toml run-control.sh control-preflight.py > CONTROL_SOURCE.sha256
ulimit -v 33554432
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=stable
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/product-order-20261019/target
cargo build --release --offline --bin factor_trace > control-build.log 2>&1
sha256sum "$CARGO_TARGET_DIR/release/factor_trace" > CONTROL_BINARY.sha256
/usr/bin/time -v "$CARGO_TARGET_DIR/release/factor_trace" ../product-pareto-20261019/parent/ops.bin public.ops.bin CONTROL-public.json > public-control.log 2>&1
/usr/bin/time -v "$CARGO_TARGET_DIR/release/factor_trace" ../product-pareto-20261019/candidate-parent4/ops.bin parent4.ops.bin CONTROL-parent4.json > parent4-control.log 2>&1
