#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/wide-cache-20261015
cd "$root"
echo $$ > single-replay.pid
trap 'rc=$?; echo "$rc" > "$root/single-replay.exit"' EXIT
ulimit -v 33554432
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
python3 prepare-single-replay.py
cd single-replay
cargo generate-lockfile --offline
cargo build --release --locked --offline > ../single-replay-build.log 2>&1
cd "$root"
base=/home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin
for mode in independent structured; do
 ./single-replay/target/release/product_paired_diagnostic "$base" single/one.bin single/one.log "$mode" "single/replay-$mode.tsv" > "single/replay-$mode.log" 2>&1
done
