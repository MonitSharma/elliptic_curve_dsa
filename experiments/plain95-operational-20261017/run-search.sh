#!/bin/bash
# PRODUCT95 ascending nonce search: 4 workers x 14 threads, lowest pass from 1, 48 h wall cap, queue mode.
set -euo pipefail
cd /home/hclau/ecdsa_research/plain95-operational-20261017
echo $$ > search.pid
trap 'echo $? > search.exit' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > search-preflight.json
export OMP_NUM_THREADS=1 RAYON_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 SEARCH_THREADS_EACH=14
ulimit -v 12582912
python3 coordinator.py > search.log 2>&1
