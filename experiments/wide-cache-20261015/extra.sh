#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/wide-cache-20261015
cd "$root"
echo $$ > extra.pid
trap 'rc=$?; echo "$rc" > "$root/extra.exit"' EXIT
ulimit -v 50331648
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
uptime
free -g
python3 prepare-extra.py
cd extra-tool
cargo build --release --locked --offline > ../extra-build.log 2>&1
cd "$root"
mkdir -p extra
base=/home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin
for mode in ur mufsr zero combo; do
 ./extra-tool/target/release/product_paired_diagnostic "$base" "$mode" "extra/$mode.bin" > "extra/$mode.log" 2>&1
 sha256sum "extra/$mode.bin" > "extra/$mode.sha256"
 /home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census "extra/$mode.bin" wide-cache-paired-v1 0 4096 16 "extra/$mode-census.jsonl" > "extra/$mode-census.log" 2>&1
done
