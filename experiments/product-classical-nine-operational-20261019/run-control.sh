#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-classical-nine-operational-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-classical-nine-operational-20261019/control.exit' EXIT
test "$(cat prepare.exit)" = 0
export RESEARCH_SLOTS=3 OMP_NUM_THREADS=1 RAYON_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python3 ../autonomous-20261019/preflight_v13.py > control-preflight.json
sha256sum control.py ACCEPTANCE.json run-control.sh ../autonomous-20261019/preflight_v13.py > CONTROL_SOURCE.sha256
ulimit -v 33554432
python3 control.py > control.log 2>&1
