#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/precision-repair-20261016
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
while [ ! -f posttable-v3.exit ];do sleep 1;done
if [ "$(cat posttable-v3.exit)" -ne 0 ];then exit 1;fi
{ hostname; date -Is; uptime; free -h; ps -eo pid,comm,nlwp,pcpu,rss,args --sort=-pcpu | head -20; } > preflight-paired-census.log
mkdir -p fresh-paired
checker=/home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census
sha256sum "$checker" ../failure-census-20261015/census/src/main.rs > fresh-paired/checker.sha256
label=public4b-precision-top1-posttable-fresh-20261016-v1
"$checker" ../product-exact-20261015/tip/ops.bin "$label" 0 4096 2 fresh-paired/parent.jsonl > fresh-paired/parent.log 2>&1 &
parent=$!;echo "$parent" > fresh-paired/parent.pid
"$checker" candidate-posttable-top1/ops.bin "$label" 0 4096 2 fresh-paired/candidate.jsonl > fresh-paired/candidate.log 2>&1 &
candidate=$!;echo "$candidate" > fresh-paired/candidate.pid
wait "$parent";pcode=$?;echo "$pcode" > fresh-paired/parent.exit
wait "$candidate";ccode=$?;echo "$ccode" > fresh-paired/candidate.exit
echo "$((pcode|ccode))" > paired-census.exit
