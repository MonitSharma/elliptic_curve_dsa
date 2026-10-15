#!/bin/bash
set -euo pipefail
root=/home/hclau/ecdsa_research/mask-evaluator-20261016
cd "$root"
trap 'echo $? > /home/hclau/ecdsa_research/mask-evaluator-20261016/reference.exit' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > reference-preflight.json
ulimit -v 16777216
python3 reference-job.py > reference-result.log 2>&1
