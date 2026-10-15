#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/wide-cache-20261015
cd "$root"
echo $$ > sweep.pid
trap 'rc=$?; echo "$rc" > "$root/sweep.exit"' EXIT
ulimit -v 50331648
uptime
free -g
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
tool=/home/hclau/ecdsa_research/cache-retention-20261015/target/release/product_paired_diagnostic
base=/home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin
mkdir -p sweep
# This is structural proof-discovery only: no evaluation inputs are used.
for cap in 512 2048 8192; do
 CACHE_ATOM_CAP="$cap" CACHE_PRODUCT_CAP=4000000 /usr/bin/time -v "$tool" "$base" "sweep/cap-$cap.bin" > "sweep/cap-$cap.log" 2>&1
 sha256sum "sweep/cap-$cap.bin" > "sweep/cap-$cap.sha256"
done
