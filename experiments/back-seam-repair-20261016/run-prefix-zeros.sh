#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/back-seam-repair-20261016
echo $$ >prefix-zeros.pid
python3 check-prefix-zeros.py >prefix-zeros.log 2>&1
status=$?;echo "$status" >prefix-zeros.exit;exit "$status"
