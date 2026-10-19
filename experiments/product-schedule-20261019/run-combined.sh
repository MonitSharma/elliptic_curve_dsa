#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product-schedule-20261019
trap 'rc=$?; printf "%s\n" "$rc" > combined.exit' EXIT
date -Is > combined-started.txt
uptime > combined-resources.txt
free -g >> combined-resources.txt
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 67108864
source /home/hclau/.cargo/env
sha256sum Cargo.toml borrow.rs recompute.rs io.rs width_pressure.rs run-combined.sh > COMBINED-SOURCE.sha256
cargo test --release --offline > combined-tests.log 2>&1
cargo build --release --offline > combined-build.log 2>&1
for cut in 1232 1230 1220; do
  target/release/recompute "borrow-$cut.ops.bin" "combined-$cut" 1024 "$cut" > "combined-$cut.log" 2>&1
  target/release/width_pressure "combined-$cut.ops.bin" "combined-width-$cut.json" > "combined-width-$cut.log" 2>&1
done
sha256sum combined-*.ops.bin > COMBINED-STREAMS.sha256
python3 summarize_combined.py
