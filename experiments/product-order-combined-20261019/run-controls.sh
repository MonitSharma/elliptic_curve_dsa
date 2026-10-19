#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-order-combined-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-order-combined-20261019/controls.exit' EXIT
test "$(cat run.exit)" = 0
python3 preflight.py > controls-preflight.json
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 33554432
tool=/home/hclau/ecdsa_research/product-order-20261019/target/release/trace_control
sha256sum "$tool" core-colored.ops.bin clean-colored.ops.bin ordered-core.ops.bin ordered-clean.ops.bin run-controls.sh > CONTROLS-SOURCE.sha256
/usr/bin/time -v "$tool" ../product-pareto-20261019/parent/ops.bin ordered-core.ops.bin core-colored.ops.bin CONTROL-CORE.json > control-core.log 2>&1
/usr/bin/time -v "$tool" ../product-pareto-20261019/parent/ops.bin ordered-clean.ops.bin clean-colored.ops.bin CONTROL-CLEAN.json > control-clean.log 2>&1
