#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product-parent-sat-20261019
trap 'rc=$?; printf "%s\n" "$rc" > roots.exit' EXIT
date -Is > roots-started.txt
uptime > roots-resources.txt
free -g >> roots-resources.txt
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 16777216
sha256sum prove_graph.py > ROOTS-SOURCE.sha256
python3 prove_graph.py test > graph-tests.log 2>&1
python3 prove_graph.py 2 roots > roots-lease-02.log 2>&1
