#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product-schedule-20261019
trap 'rc=$?; printf "%s\n" "$rc" > refined.exit' EXIT
date -Is > refined-started.txt
uptime > refined-resources.txt
free -g >> refined-resources.txt
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 67108864
source /home/hclau/.cargo/env
sha256sum Cargo.toml borrow.rs recolor.rs recompute.rs io.rs width_pressure.rs run-refined.sh > REFINED-SOURCE.sha256
cargo test --release --offline > refined-tests.log 2>&1
cargo build --release --offline > refined-build.log 2>&1
for cut in 1232 1230; do
  test -f "combined-width-$cut.json"
  target/release/borrow "combined-$cut.ops.bin" "$cut" "refined-$cut" > "refined-$cut.log" 2>&1
  target/release/width_pressure "refined-$cut.ops.bin" "refined-width-$cut.json" > "refined-width-$cut.log" 2>&1
done
sha256sum refined-*.ops.bin > REFINED-STREAMS.sha256
