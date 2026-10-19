#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-support-tight-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-support-tight-20261019/run.exit' EXIT
python3 preflight.py > preflight.json
sha256sum tight_color.rs io.rs Cargo.toml preflight.py run.sh > SOURCE.sha256
ulimit -v 33554432
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=stable
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/product-order-20261019/target
cargo test --release --offline --bin tight_color > tests.log 2>&1
cargo build --release --offline --bin tight_color > build.log 2>&1
sha256sum Cargo.lock "$CARGO_TARGET_DIR/release/tight_color" "$CARGO_TARGET_DIR/release/trace_control" "$CARGO_TARGET_DIR/release/mapped_trace" > BINARY.sha256
parent=../product-pareto-20261019/parent/ops.bin
/usr/bin/time -v "$CARGO_TARGET_DIR/release/tight_color" "$parent" original-tight > original-tight.log 2>&1
/usr/bin/time -v "$CARGO_TARGET_DIR/release/trace_control" "$parent" "$parent" original-tight.ops.bin CONTROL-ORIGINAL.json > control-original.log 2>&1
/usr/bin/time -v "$CARGO_TARGET_DIR/release/tight_color" ../product-order-combined-20261019/ordered-clean.ops.bin scheduled-tight > scheduled-tight.log 2>&1
/usr/bin/time -v "$CARGO_TARGET_DIR/release/trace_control" "$parent" ../product-order-combined-20261019/ordered-clean.ops.bin scheduled-tight.ops.bin CONTROL-SCHEDULED.json > control-scheduled.log 2>&1
/usr/bin/time -v "$CARGO_TARGET_DIR/release/tight_color" ../product-mr-order-20261019/ordered-core.ops.bin mr-tight > mr-tight.log 2>&1
/usr/bin/time -v "$CARGO_TARGET_DIR/release/mapped_trace" "$parent" ../product-mr-order-20261019/ordered-core.ops.bin mr-tight.ops.bin ../product-mr-order-20261019/ordered-core.rng-map.bin ../product-mr-order-20261019/ordered-core.permutation.bin CONTROL-MR.json > control-mr.log 2>&1
