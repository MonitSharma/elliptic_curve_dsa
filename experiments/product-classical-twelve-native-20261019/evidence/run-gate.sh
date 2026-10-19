#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-classical-twelve-native-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-classical-twelve-native-20261019/gate.exit' EXIT
export RESEARCH_SLOTS=3 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 RAYON_NUM_THREADS=1
python3 ../autonomous-20261019/preflight_v12.py > gate-preflight.json
sha256sum qualify.py run-gate.sh refresh_record.py GATE-PLAN.md ../autonomous-20261019/preflight_v12.py > GATE_SOURCE.sha256
ulimit -v 33554432
python3 qualify.py
