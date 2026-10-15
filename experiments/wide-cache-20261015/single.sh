#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/wide-cache-20261015
cd "$root"
echo $$ > single.pid
trap 'rc=$?; echo "$rc" > "$root/single.exit"' EXIT
ulimit -v 50331648
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
uptime
free -g
python3 prepare-single.py
cd single-tool
cargo test --release --locked --offline lazy_single_ -- --nocapture > ../single-tests.log 2>&1
cargo build --release --locked --offline > ../single-build.log 2>&1
cd "$root"
mkdir -p single
base=/home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin
/usr/bin/time -v ./single-tool/target/release/product_paired_diagnostic "$base" 1 single/one.bin > single/one.log 2>&1
sha256sum single/one.bin > single/one.sha256
