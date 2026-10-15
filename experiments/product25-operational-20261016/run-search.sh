#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product25-operational-20261016
echo $$ > search.pid
trap 'echo $? > search.exit' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > search-preflight.json
export OMP_NUM_THREADS=1 RAYON_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 SEARCH_THREADS_EACH=12
ulimit -v 12582912
python3 coordinator.py > search.log 2>&1
