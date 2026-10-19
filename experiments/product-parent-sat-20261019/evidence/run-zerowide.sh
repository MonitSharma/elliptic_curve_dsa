#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product-parent-sat-20261019
trap 'rc=$?; printf "%s\n" "$rc" > zerowide.exit' EXIT
date -Is > zerowide-started.txt
uptime > zerowide-resources.txt
free -g >> zerowide-resources.txt
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 16777216
sha256sum prove_zero.py extract_zero_wider.py run_zero_wider.py run-zerowide.sh > ZERO-WIDER-SOURCE.sha256
python3 extract_zero_wider.py > zero-wider-extract.log 2>&1
python3 run_zero_wider.py > zero-wider-screen.log 2>&1
