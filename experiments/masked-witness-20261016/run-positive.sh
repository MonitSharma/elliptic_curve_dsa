#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/masked-witness-20261016
echo $$ > positive.pid
trap 'echo $? > positive.exit' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > positive-preflight.json
export OMP_NUM_THREADS=1 RAYON_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 16777216
python3 positive.py > positive-validation.log 2>&1
