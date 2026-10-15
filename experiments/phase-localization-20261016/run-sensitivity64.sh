#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/phase-localization-20261016
echo $$ >sensitivity64.pid
{ hostname;date -Is;free -h;ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -15; } >preflight-sensitivity64.log
# Static partition: all remaining witnesses in original census order, no early stop.
for worker in 0 1 2 3 4 5 6 7;do
 (
  for ((lane=4+worker;lane<64;lane+=8));do
   ./sensitivity "$lane" 0 >"sensitivity-$lane-0.jsonl" 2>"sensitivity-$lane-0.log"
   echo $? >"sensitivity-$lane-0.exit"
  done
 ) &
done
wait
echo 0 >sensitivity64-wrapper.exit
