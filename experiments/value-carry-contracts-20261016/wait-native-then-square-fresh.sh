#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/value-carry-contracts-20261016
echo $$ > square-qualification.pid
while [ ! -f square-native.exit ];do sleep 10;done
test "$(cat square-native.exit)" = 0 || exit 1
python3 verify-square-native.py >square-native-verification.log 2>&1
code=$?;echo "$code" >square-native-verification.exit
if [ "$code" -ne 0 ];then echo "$code" >square-qualification.exit;exit "$code";fi
bash run-square-fresh.sh >square-fresh-launch.log 2>&1
code=$?
if [ "$code" -ne 0 ];then echo "$code" >square-qualification.exit;exit "$code";fi
python3 summarize-square-paired.py >square-paired-summary.log 2>&1
code=$?;echo "$code" >square-paired-summary.exit;echo "$code" >square-qualification.exit
exit "$code"
