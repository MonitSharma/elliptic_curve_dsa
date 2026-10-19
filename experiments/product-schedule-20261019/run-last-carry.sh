#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product-schedule-20261019
trap 'rc=$?; printf "%s\n" "$rc" > last-carry.exit' EXIT
uptime > last-carry-resources.txt
free -g >> last-carry-resources.txt
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 67108864
source /home/hclau/.cargo/env
sha256sum Cargo.toml borrow.rs recolor.rs recompute.rs io.rs width_pressure.rs > LAST-CARRY-SOURCE.sha256
cargo test --release --offline > last-carry-tests.log 2>&1
cargo build --release --offline > last-carry-build.log 2>&1
for cut in 1232 1230; do
  target/release/borrow "refined-$cut.ops.bin" "$cut" "last-carry-$cut" > "last-carry-$cut.log" 2>&1
  target/release/width_pressure "last-carry-$cut.ops.bin" "last-carry-width-$cut.json" > "last-carry-width-$cut.log" 2>&1
done
sha256sum last-carry-*.ops.bin > LAST-CARRY-STREAMS.sha256
