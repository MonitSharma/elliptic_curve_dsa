#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/census-control-family-20261016
echo $$ > run.pid
trap 'echo $? > run.exit' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json
ulimit -v 16777216
/usr/bin/time -v timeout 600 python3 inventory.py > inventory.log 2>&1
