#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/mask-evaluator-20261016
trap 'echo $? > compact.exit' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > compact-preflight.json
ulimit -v 16777216
python3 compact-job.py > compact-result.log 2>&1
