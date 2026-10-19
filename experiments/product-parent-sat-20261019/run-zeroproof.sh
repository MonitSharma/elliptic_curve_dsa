#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product-parent-sat-20261019
trap 'rc=$?; printf "%s\n" "$rc" > zeroproof.exit' EXIT
date -Is > zeroproof-started.txt
uptime > zeroproof-resources.txt
free -g >> zeroproof-resources.txt
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 16777216
sha256sum prove_zero.py extract_zero.py run_zero_proofs.py run-zeroproof.sh > ZERO-PROOF-SOURCE.sha256
python3 prove_zero.py test > zero-proof-tests.log 2>&1
python3 extract_zero.py > zero-proof-extract.log 2>&1
python3 run_zero_proofs.py > zero-proof-screen.log 2>&1
