#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/census-deletion-family-20261016
ulimit -v 16777216
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
date -u > started.utc
sha256sum inventory-deletions.py > script-before.sha256
timeout 300s /usr/bin/time -v python3 inventory-deletions.py > inventory.log 2>&1
code=$?
echo "$code" > inventory.exit
sha256sum inventory-deletions.py > script-after.sha256
date -u > finished.utc
exit "$code"
