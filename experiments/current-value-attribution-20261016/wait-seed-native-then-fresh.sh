#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/seed-restore-20261016
echo $$ >qualification.pid
while [ ! -f native.exit ];do sleep 10;done
test "$(cat native.exit)" = 0 || exit 1
python3 ../current-value-attribution-20261016/verify-seed-native.py >native-verification.log 2>&1
code=$?;echo "$code" >native-verification.exit
if [ "$code" -ne 0 ];then echo "$code" >qualification.exit;exit "$code";fi
# Keep at most one four-worker census under this agent after Square4 finishes.
while [ ! -f ../value-carry-contracts-20261016/square-fresh.exit ];do sleep 15;done
bash ../current-value-attribution-20261016/run-seed-fresh.sh >fresh-launch.log 2>&1
code=$?;if [ "$code" -ne 0 ];then echo "$code" >qualification.exit;exit "$code";fi
python3 summarize-seed-paired.py >paired-summary.log 2>&1
code=$?;echo "$code" >paired-summary.exit;echo "$code" >qualification.exit;exit "$code"
