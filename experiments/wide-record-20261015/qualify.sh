#!/usr/bin/env bash
# Queue only: never invokes the external submission CLI.
set -euo pipefail
root=/home/hclau/ecdsa_research/wide-record-20261015
up=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > qualify.pid
trap 'rc=$?; echo "$rc" > "$root/qualify.exit"' EXIT
while test ! -f "$up/wide-final.exit"; do sleep 5; done
python3 prepare.py > prepare.log 2>&1
python3 /home/hclau/ecdsa_research/server-preflight.py > evidence/screen-preflight.json
ulimit -v 50331648
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
/usr/bin/time -v /home/hclau/ecdsa_research/nonce-screen-20261015/screen/target/release/nonce_screen "$up/wide-candidate-final/ops.bin" 1 20000 16 evidence/screen.jsonl > evidence/screen.out 2> evidence/screen.err
python3 select.py
cd "$up/wide-candidate-final"
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/evidence/benchmark-preflight.json"
set +e
/usr/bin/time -v ./benchmark.sh > "$root/evidence/benchmark.log" 2>&1
rc=$?
set -e
echo "$rc" > "$root/evidence/benchmark.exit"
if test -f results.tsv; then cp results.tsv "$root/evidence/benchmark-results.tsv"; fi
git restore --source=HEAD -- results.tsv
test "$rc" = 0
cp score.json "$root/evidence/score.json"
python3 "$root/finalize.py"
# Fixed final paired sample, declared before selecting the nonce; no early stopping.
C=/home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/evidence/final-census-preflight.json"
"$C" /home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin wide-four-stage-final-20261015 0 16384 8 "$root/evidence/final-parent-census.jsonl" > "$root/evidence/final-parent-census.log" 2>&1 &
p1=$!; echo "$p1" > "$root/evidence/final-parent-census.pid"
"$C" ops.bin wide-four-stage-final-20261015 0 16384 8 "$root/evidence/final-census.jsonl" > "$root/evidence/final-census.log" 2>&1 &
p2=$!; echo "$p2" > "$root/evidence/final-census.pid"
wait "$p1"
wait "$p2"
date -Is > "$root/evidence/completed-at.txt"
