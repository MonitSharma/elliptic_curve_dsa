#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/precision-family-20261016
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
if [ ! -f candidate.exit ] || [ "$(cat candidate.exit)" -ne 0 ];then echo 'full candidate not ready' > fresh-paired.launch-rejected;exit 1;fi
mkdir -p fresh-paired
{ hostname;date -Is;uptime;free -h;ps -eo pid,comm,nlwp,pcpu,rss,args --sort=-pcpu | head -20; } > fresh-paired/preflight.log
checker=/home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census
sha256sum "$checker" ../failure-census-20261015/census/src/main.rs candidate/ops.bin ../product-exact-20261015/tip/ops.bin > fresh-paired/source-checker.sha256
label=public4b-precision-familyA29-independent-20261016-v1
echo "$label" > fresh-paired/input-label.txt
"$checker" ../product-exact-20261015/tip/ops.bin "$label" 0 4096 4 fresh-paired/parent.jsonl > fresh-paired/parent.log 2>&1 &
parent=$!;echo "$parent" > fresh-paired/parent.pid
"$checker" candidate/ops.bin "$label" 0 4096 4 fresh-paired/candidate.jsonl > fresh-paired/candidate.log 2>&1 &
candidate=$!;echo "$candidate" > fresh-paired/candidate.pid
wait "$parent";pcode=$?;echo "$pcode" > fresh-paired/parent.exit
wait "$candidate";ccode=$?;echo "$ccode" > fresh-paired/candidate.exit
echo "$((pcode|ccode))" > fresh-paired.exit
