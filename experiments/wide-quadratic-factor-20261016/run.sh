#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/wide-quadratic-factor-20261016
echo $$ > run.pid
trap 'echo $? > run.exit' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json
ulimit -v 16777216
/usr/bin/time -v timeout 300 python3 census.py > census.log 2>&1
