#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/seam-phase-repair-20261016
echo $$ >fresh-paired.pid
while [ ! -f proofs.exit ];do sleep 5;done
[ "$(cat proofs.exit)" = 0 ] || exit 1
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
mkdir -p fresh-paired
{ hostname;date -Is;free -h;ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -15; } >fresh-paired/preflight.log
checker=/home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census
sha256sum "$checker" ../failure-census-20261015/census/src/main.rs candidate/ops.bin ../product-exact-20261015/tip/ops.bin >fresh-paired/source-checker.sha256
label=public4b-frontseam-classical-borrow20to21-independent-20261016-v1
echo "$label" >fresh-paired/input-label.txt
"$checker" ../product-exact-20261015/tip/ops.bin "$label" 0 4096 2 fresh-paired/parent.jsonl >fresh-paired/parent.log 2>&1 &
parent=$!;echo "$parent" >fresh-paired/parent.pid
"$checker" candidate/ops.bin "$label" 0 4096 2 fresh-paired/candidate.jsonl >fresh-paired/candidate.log 2>&1 &
candidate=$!;echo "$candidate" >fresh-paired/candidate.pid
wait "$parent";pcode=$?;echo "$pcode" >fresh-paired/parent.exit
wait "$candidate";ccode=$?;echo "$ccode" >fresh-paired/candidate.exit
echo "$((pcode|ccode))" >fresh-paired.exit
