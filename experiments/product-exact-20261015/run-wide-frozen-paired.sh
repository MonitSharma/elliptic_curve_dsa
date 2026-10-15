#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > wide-frozen-paired.pid
trap 'rc=$?; echo "$rc" > wide-frozen-paired.exit' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 41943040
C=/home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census
python3 /home/hclau/ecdsa_research/server-preflight.py > wide-frozen-parent-preflight.json
/usr/bin/time -v "$C" /home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin wide-frozen-four-stage-20261015 0 4096 4 wide-frozen-parent-census.jsonl > wide-frozen-parent-census.out 2> wide-frozen-parent-census.err &
p1=$!; echo "$p1" > wide-frozen-parent-census.pid
python3 /home/hclau/ecdsa_research/server-preflight.py > wide-frozen-candidate-preflight.json
/usr/bin/time -v "$C" wide-chain-retained.bin wide-frozen-four-stage-20261015 0 4096 4 wide-frozen-candidate-census.jsonl > wide-frozen-candidate-census.out 2> wide-frozen-candidate-census.err &
p2=$!; echo "$p2" > wide-frozen-candidate-census.pid
set +e
wait "$p1"; a=$?; echo "$a" > wide-frozen-parent-census.exit
wait "$p2"; b=$?; echo "$b" > wide-frozen-candidate-census.exit
set -e
test "$a" = 0 && test "$b" = 0
