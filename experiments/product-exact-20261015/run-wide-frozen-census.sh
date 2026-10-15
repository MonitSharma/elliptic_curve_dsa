#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > wide-frozen-census.pid
trap 'rc=$?; echo "$rc" > wide-frozen-census.exit' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 41943040
until test -f frozen-deep.exit; do sleep 5; done
python3 /home/hclau/ecdsa_research/server-preflight.py > wide-frozen-census-preflight.json
/usr/bin/time -v /home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census wide-chain-retained.bin wide-cache-paired-v1 0 4096 12 wide-final-census.jsonl > wide-final-census.out 2> wide-final-census.err
