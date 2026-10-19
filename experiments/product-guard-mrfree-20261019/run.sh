#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-guard-mrfree-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-guard-mrfree-20261019/run.exit' EXIT
while [ ! -f ../product-guard-schedule-20261019/control.exit ]; do sleep 15; done
test "$(cat ../product-guard-schedule-20261019/control.exit)" = 0
python3 preflight.py > preflight.json
sha256sum guard_mrfree.rs guard_mapped_trace.rs tight_annotated.rs io.rs Cargo.toml run.sh preflight.py prepare.py > SOURCE.sha256
ulimit -v 33554432
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=stable
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/product-order-20261019/target
cargo test --release --offline --bins > tests.log 2>&1
cargo build --release --offline --bins > build.log 2>&1
sha256sum Cargo.lock "$CARGO_TARGET_DIR/release/guard_mrfree" "$CARGO_TARGET_DIR/release/guard_mapped_trace" "$CARGO_TARGET_DIR/release/guard_strong_annotated" > BINARY.sha256
/usr/bin/time -v "$CARGO_TARGET_DIR/release/guard_strong_annotated" ../product-pareto-20261019/parent/ops.bin annotations > annotations.log 2>&1
python3 qualify_annotations.py > ANNOTATION-CONTROL.json
for mode in prior strong; do
  clean=../product-order-combined-20261019/annotations.clean-events.bin
  if [ "$mode" = strong ]; then clean=annotations.clean-events.bin; fi
  /usr/bin/time -v "$CARGO_TARGET_DIR/release/guard_mrfree" ../product-pareto-20261019/parent/ops.bin "$mode" "$clean" > "$mode-schedule.log" 2>&1
  /usr/bin/time -v "$CARGO_TARGET_DIR/release/tight_color" "$mode.ordered.ops.bin" "$mode-tight" > "$mode-color.log" 2>&1
  /usr/bin/time -v "$CARGO_TARGET_DIR/release/guard_mapped_trace" ../product-pareto-20261019/parent/ops.bin "$mode.converted.ops.bin" "$mode.ordered.ops.bin" "$mode-tight.ops.bin" "$mode.rng-map.bin" "CONTROL-$mode.json" > "$mode-control.log" 2>&1
done
