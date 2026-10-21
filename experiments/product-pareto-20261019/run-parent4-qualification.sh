#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product-pareto-20261019
test ! -e parent4-qualification.pid
echo $$ > parent4-qualification.pid
trap 'echo $? > parent4-qualification.exit' EXIT
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
python3 -u qualify_parent4.py
