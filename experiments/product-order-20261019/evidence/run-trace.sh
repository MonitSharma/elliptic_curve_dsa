#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-order-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-order-20261019/trace.exit' EXIT
test "$(cat run-v3.exit)" = 0
python3 preflight-v2.py > trace-preflight.json
sha256sum trace-tool/trace.rs trace-tool/Cargo.toml run-trace.sh > TRACE-SOURCE.sha256
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=stable
CARGO_TARGET_DIR="$r/target" cargo build --release --offline --manifest-path trace-tool/Cargo.toml > trace-build.log 2>&1
sha256sum target/release/trace_control > TRACE-BINARY.sha256
/usr/bin/time -v target/release/trace_control ../product-pareto-20261019/parent/ops.bin reordered.ops.bin recolored.ops.bin TRACE-CONTROL.json > trace.log 2>&1
