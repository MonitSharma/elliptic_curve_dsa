#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-copy-cache-filter-20261020
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-copy-cache-filter-20261020/qualification.exit' EXIT
export RESEARCH_SLOTS=3 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 RAYON_NUM_THREADS=1
python3 ../autonomous-20261019/preflight_v15.py > qualification-preflight.json
sha256sum validate_gate.py validate.py run-qualify.sh ../autonomous-20261019/preflight_v15.py > QUALIFICATION_SOURCE.sha256
ulimit -v 33554432
python3 validate_gate.py
