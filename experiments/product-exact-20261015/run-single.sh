#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > single.pid
trap 'rc=$?; echo "$rc" > single.exit' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 62914560
python3 /home/hclau/ecdsa_research/server-preflight.py > single-preflight.json
/usr/bin/time -v /home/hclau/ecdsa_research/wide-cache-20261015/single-tool/target/release/product_paired_diagnostic tip/ops.bin 4 single-4.bin > single-4-generate.log 2>&1
sha256sum single-4.bin > single-4.sha256
until test -f conditional.exit; do sleep 5; done
python3 /home/hclau/ecdsa_research/server-preflight.py > single-census-preflight.json
/usr/bin/time -v /home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census single-4.bin product-exact-20261015 0 4096 12 single-4-census.jsonl > single-4-census.out 2> single-4-census.err
