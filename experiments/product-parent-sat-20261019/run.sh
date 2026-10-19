#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product-parent-sat-20261019
trap 'rc=$?; printf "%s\n" "$rc" > run.exit' EXIT
date -Is > started.txt
uptime > resources.txt
free -g >> resources.txt
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 33554432
python3 install.py > install.log 2>&1
python3 prove.py test > tests.log 2>&1
python3 extract.py > extract.log 2>&1
python3 prove.py 2 > lease-02.log 2>&1
