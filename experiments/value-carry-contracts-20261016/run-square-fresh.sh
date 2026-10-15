#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/value-carry-contracts-20261016
echo $$ >square-fresh.pid
test "$(cat square-native-verification.exit)" = 0 || exit 1
test "$(cat protected-dirty-square.exit)" = 0 || exit 1
test "$(cat square-guard-tests.exit)" = 0 || exit 1
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
mkdir square-fresh
{ hostname;date -Is;uptime;free -h;ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -20; } >square-fresh/preflight.log
checker=/home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census
sha256sum "$checker" ../failure-census-20261015/census/src/main.rs square4-candidate/ops.bin ../product-exact-20261015/tip/ops.bin >square-fresh/source-checker.sha256
label=public4b-all-C130-square-dirty-carry-independent-20261016-v1
echo "$label" >square-fresh/input-label.txt
"$checker" ../product-exact-20261015/tip/ops.bin "$label" 0 32768 4 square-fresh/parent.jsonl >square-fresh/parent.log 2>&1 &
parent=$!;echo "$parent" >square-fresh/parent.pid
wait "$parent";code=$?;echo "$code" >square-fresh/parent.exit
if [ "$code" -ne 0 ];then echo "$code" >square-fresh.exit;exit "$code";fi
"$checker" square4-candidate/ops.bin "$label" 0 32768 4 square-fresh/candidate.jsonl >square-fresh/candidate.log 2>&1 &
candidate=$!;echo "$candidate" >square-fresh/candidate.pid
wait "$candidate";code=$?;echo "$code" >square-fresh/candidate.exit
echo "$code" >square-fresh.exit
exit "$code"
