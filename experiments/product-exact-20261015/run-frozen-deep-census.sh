#!/usr/bin/env bash
# Fixed 32,768-batch census per source, including the first 4,096 batches.
# The sample size is declared before continuation results; never stop on a pass.
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > frozen-deep.pid
trap 'rc=$?; echo "$rc" > frozen-deep.exit' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 41943040
C=/home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census
python3 /home/hclau/ecdsa_research/server-preflight.py > frozen-deep-parent-preflight.json
/usr/bin/time -v "$C" tip/ops.bin product-frozen-four-stage-20261015 4096 28672 10 frozen-parent-continuation.jsonl > frozen-parent-continuation.out 2> frozen-parent-continuation.err &
p1=$!; echo "$p1" > frozen-parent-continuation.pid
python3 /home/hclau/ecdsa_research/server-preflight.py > frozen-deep-candidate-preflight.json
/usr/bin/time -v "$C" chain-retained.bin product-frozen-four-stage-20261015 4096 28672 10 frozen-candidate-continuation.jsonl > frozen-candidate-continuation.out 2> frozen-candidate-continuation.err &
p2=$!; echo "$p2" > frozen-candidate-continuation.pid
set +e
wait "$p1"; a=$?; echo "$a" > frozen-parent-continuation.exit
wait "$p2"; b=$?; echo "$b" > frozen-candidate-continuation.exit
set -e
test "$a" = 0 && test "$b" = 0
python3 combine_deep_census.py
