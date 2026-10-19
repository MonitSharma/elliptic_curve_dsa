#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-classical-twelve-filter-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-classical-twelve-filter-20261019/qualification.exit' EXIT
export RESEARCH_SLOTS=3 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 RAYON_NUM_THREADS=1
python3 ../autonomous-20261019/preflight_v14.py > qualification-preflight.json
sha256sum validate_gate.py validate.py run-qualify.sh ../autonomous-20261019/preflight_v14.py > QUALIFICATION_SOURCE.sha256
ulimit -v 33554432
python3 validate_gate.py
