#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > final-census.pid
trap 'rc=$?; echo "$rc" > final-census.exit' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 41943040
python3 -c 'import json,hashlib;from pathlib import Path;r=json.load(open("FREEZE.json"));assert hashlib.sha256(Path("chain-retained.bin").read_bytes()).hexdigest()==r["external_stream_sha256"]'
C=/home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census
until test -f extended.exit; do sleep 5; done
python3 /home/hclau/ecdsa_research/server-preflight.py > frozen-parent-preflight.json
/usr/bin/time -v "$C" tip/ops.bin product-frozen-four-stage-20261015 0 4096 10 frozen-parent-census.jsonl > frozen-parent-census.out 2> frozen-parent-census.err &
p1=$!; echo "$p1" > frozen-parent-census.pid
python3 /home/hclau/ecdsa_research/server-preflight.py > frozen-candidate-preflight.json
/usr/bin/time -v "$C" chain-retained.bin product-frozen-four-stage-20261015 0 4096 10 frozen-candidate-census.jsonl > frozen-candidate-census.out 2> frozen-candidate-census.err &
p2=$!; echo "$p2" > frozen-candidate-census.pid
set +e
wait "$p1"; a=$?; echo "$a" > frozen-parent-census.exit
wait "$p2"; b=$?; echo "$b" > frozen-candidate-census.exit
set -e
test "$a" = 0 && test "$b" = 0
