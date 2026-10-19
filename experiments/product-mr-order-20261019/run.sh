#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-mr-order-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-mr-order-20261019/run.exit' EXIT
python3 preflight.py > preflight.json
sha256sum order_mrfree.rs mapped_trace.rs legacy.rs io.rs Cargo.toml preflight.py run.sh > SOURCE.sha256
ulimit -v 33554432
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=stable
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/product-order-20261019/target
cargo test --release --offline --bins > tests.log 2>&1
cargo build --release --offline --bins > build.log 2>&1
sha256sum Cargo.lock "$CARGO_TARGET_DIR/release/order_mrfree" "$CARGO_TARGET_DIR/release/mapped_trace" "$CARGO_TARGET_DIR/release/guard_annotated" > BINARY.sha256
/usr/bin/time -v "$CARGO_TARGET_DIR/release/order_mrfree" ../product-pareto-20261019/parent/ops.bin ordered-core core > ordered-core.log 2>&1
/usr/bin/time -v "$CARGO_TARGET_DIR/release/guard_annotated" ordered-core.ops.bin core-colored > core-colored.log 2>&1
/usr/bin/time -v "$CARGO_TARGET_DIR/release/mapped_trace" ../product-pareto-20261019/parent/ops.bin ordered-core.ops.bin core-colored.ops.bin ordered-core.rng-map.bin ordered-core.permutation.bin CONTROL-CORE.json > control-core.log 2>&1
/usr/bin/time -v "$CARGO_TARGET_DIR/release/order_mrfree" ../product-pareto-20261019/parent/ops.bin ordered-clean clean ../product-order-combined-20261019/annotations.clean-events.bin > ordered-clean.log 2>&1
/usr/bin/time -v "$CARGO_TARGET_DIR/release/guard_annotated" ordered-clean.ops.bin clean-colored > clean-colored.log 2>&1
/usr/bin/time -v "$CARGO_TARGET_DIR/release/mapped_trace" ../product-pareto-20261019/parent/ops.bin ordered-clean.ops.bin clean-colored.ops.bin ordered-clean.rng-map.bin ordered-clean.permutation.bin CONTROL-CLEAN.json > control-clean.log 2>&1
