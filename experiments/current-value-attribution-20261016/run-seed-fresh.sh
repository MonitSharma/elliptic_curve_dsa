#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/seed-restore-20261016
echo $$ >fresh.pid
test "$(cat native-verification.exit)" = 0 || exit 1
test "$(cat protected.exit)" = 0 || exit 1
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
mkdir seed-fresh
{ hostname;date -Is;uptime;free -h;ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -18; } >seed-fresh/preflight.log
checker=/home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census
sha256sum "$checker" ../failure-census-20261015/census/src/main.rs candidate/ops.bin ../product-exact-20261015/tip/ops.bin >seed-fresh/source-checker.sha256
label=public4b-all-seed-dropped-control-restore-independent-20261016-v1
echo "$label" >seed-fresh/input-label.txt
"$checker" ../product-exact-20261015/tip/ops.bin "$label" 0 32768 4 seed-fresh/parent.jsonl >seed-fresh/parent.log 2>&1 &
parent=$!;echo "$parent" >seed-fresh/parent.pid
wait "$parent";code=$?;echo "$code" >seed-fresh/parent.exit
if [ "$code" -ne 0 ];then echo "$code" >seed-fresh.exit;exit "$code";fi
"$checker" candidate/ops.bin "$label" 0 32768 4 seed-fresh/candidate.jsonl >seed-fresh/candidate.log 2>&1 &
candidate=$!;echo "$candidate" >seed-fresh/candidate.pid
wait "$candidate";code=$?;echo "$code" >seed-fresh/candidate.exit;echo "$code" >seed-fresh.exit;exit "$code"
