#!/bin/bash
set -euo pipefail
root=/home/hclau/ecdsa_research/failure-floor-20261015
cd "$root"
echo $$ > window4.pid
trap 's=$?; echo "$s" > "$root/window4.exit"' EXIT
ulimit -v 62914560
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 RUSTUP_TOOLCHAIN=1.93.0 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > window4-preflight.json
python3 prepare-window.py > window4-prepare.log 2>&1
cd window4-b3
cargo build --release --locked --offline --bin build_circuit > ../window4-build.log 2>&1
/usr/bin/time -v target/release/build_circuit > ../window4-generate.log 2>&1
sha256sum ops.bin > ../window4-stream.sha256
cd "$root"
census=/home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census
"$census" window4-b3/ops.bin failure-floor-window4 0 4096 8 window4-census.jsonl > window4-census.log 2>&1 &
"$census" /home/hclau/ecdsa_research/dynamic-pool-20261015/wide-b3/ops.bin failure-floor-window4 0 4096 8 parent-window4-census.jsonl > parent-window4-census.log 2>&1 &
wait
