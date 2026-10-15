#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/wide-cache-20261015
cd "$root"
echo $$ > intern.pid
trap 'rc=$?; echo "$rc" > "$root/intern.exit"' EXIT
ulimit -v 50331648
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
uptime
free -g
python3 prepare-intern.py
cd intern-tool
cargo test --release --locked --offline intern_tests -- --nocapture > ../intern-tests.log 2>&1
cargo build --release --locked --offline > ../intern-build.log 2>&1
cd "$root"
mkdir -p intern
base=/home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin
for cap in 32 128 512; do
 CACHE_ATOM_CAP="$cap" CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./intern-tool/target/release/product_paired_diagnostic "$base" "intern/cap-$cap.bin" > "intern/cap-$cap.log" 2>&1
 sha256sum "intern/cap-$cap.bin" > "intern/cap-$cap.sha256"
done
