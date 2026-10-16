#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/current-value-attribution-20261016
echo $$ >seed-replay-coordinator.pid
while [ ! -f seed-markers.exit ]; do sleep 15; done
code=$(cat seed-markers.exit)
if [ "$code" -ne 0 ]; then echo "$code" >seed-replay-coordinator.exit; exit "$code"; fi
expected=ff5163962ff5337753235d79f4026893e35b0445ae7406bf03be76d8a3d27a69
actual=$(sha256sum raw-seed-builder.bin | cut -d' ' -f1)
if [ "$actual" != "$expected" ]; then echo "raw stream mismatch $actual"; echo 91 >seed-replay-coordinator.exit;exit 91;fi
bash run-seed-attribution.sh
code=$?;echo "$code" >seed-replay-coordinator.exit;exit "$code"
