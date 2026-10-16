#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/quantum-borrow-family-20261016
echo $$ >wait-native-then-fresh.pid
while [ ! -f native-verification.exit ];do
 if [ -f native.exit ] && [ "$(cat native.exit)" != 0 ];then echo 1 >wait-native-then-fresh.exit;exit 1;fi
 sleep 5
done
while [ ! -f quantum-proofs.exit ];do sleep 5;done
test "$(cat native-verification.exit)" = 0 || exit 1
test "$(cat quantum-proofs.exit)" = 0 || exit 1
bash run-flag-fresh.sh >fresh-launch.log 2>&1
status=$?; echo $status >wait-native-then-fresh.exit; [ "$status" = 0 ] || exit "$status"
python3 summarize-flag-paired.py >paired-summary.log 2>&1
status=$?; echo $status >paired-summary.exit; exit "$status"
