#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product-parent-sat-20261019
trap 'rc=$?; printf "%s\n" "$rc" > wide.exit' EXIT
date -Is > wide-started.txt
uptime > wide-resources.txt
free -g >> wide-resources.txt
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 16777216
sha256sum prove_wide.py extract_wide.py run_wide.py run-wide.sh > WIDE-SOURCE.sha256
python3 prove_wide.py test > wide-tests.log 2>&1
python3 extract_wide.py > wide-extract.log 2>&1
python3 run_wide.py > wide-screen.log 2>&1
