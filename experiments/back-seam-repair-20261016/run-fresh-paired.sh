#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/back-seam-repair-20261016
echo $$ >fresh-paired.pid
while [ ! -f native-verification.exit ];do sleep 5;done
[ "$(cat native-verification.exit)" = 0 ] || exit 1
[ "$(cat phase-proofs.exit)" = 0 ] || exit 1
python3 verify-local-proofs.py >verify-local-proofs.log 2>&1
status=$?;echo "$status" >verify-local-proofs.exit;[ "$status" = 0 ] || exit "$status"
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
mkdir -p fresh-paired
{ hostname;date -Is;free -h;ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -15; } >fresh-paired/preflight.log
checker=/home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census
sha256sum "$checker" ../failure-census-20261015/census/src/main.rs candidate/ops.bin ../product-exact-20261015/tip/ops.bin >fresh-paired/source-checker.sha256
label=public4b-both-backseams-classical-borrow20to21-independent-20261016-v1
echo "$label" >fresh-paired/input-label.txt
"$checker" ../product-exact-20261015/tip/ops.bin "$label" 0 4096 2 fresh-paired/parent.jsonl >fresh-paired/parent.log 2>&1 &
parent=$!;echo "$parent" >fresh-paired/parent.pid
"$checker" candidate/ops.bin "$label" 0 4096 2 fresh-paired/candidate.jsonl >fresh-paired/candidate.log 2>&1 &
candidate=$!;echo "$candidate" >fresh-paired/candidate.pid
wait "$parent";pcode=$?;echo "$pcode" >fresh-paired/parent.exit
wait "$candidate";ccode=$?;echo "$ccode" >fresh-paired/candidate.exit
echo "$((pcode|ccode))" >fresh-paired.exit
