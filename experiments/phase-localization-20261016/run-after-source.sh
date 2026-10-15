#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/phase-localization-20261016
echo $$ >after-source.pid
while [ ! -f source-map.exit ];do sleep 5;done
[ "$(cat source-map.exit)" = 0 ] || exit 1
echo 'ff5163962ff5337753235d79f4026893e35b0445ae7406bf03be76d8a3d27a69  raw-builder.bin' | sha256sum -c - >source-raw-verification.log 2>&1
status=$?;echo $status >source-raw-verification.exit;[ "$status" = 0 ] || exit "$status"
bash run-sensitivity64.sh
status=$?;echo $status >after-source.exit;exit "$status"
