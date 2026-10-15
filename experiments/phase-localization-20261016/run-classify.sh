#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/phase-localization-20261016
echo $$ >classify.pid
while [ ! -f sensitivity64-wrapper.exit ];do sleep 5;done
python3 classify-hits.py >phase-sensitivity-classification.log 2>&1
status=$?;echo $status >classify.exit;exit "$status"
