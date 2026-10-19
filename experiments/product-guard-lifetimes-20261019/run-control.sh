#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-guard-lifetimes-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-guard-lifetimes-20261019/control.exit' EXIT
test "$(cat run.exit)" = 0
python3 preflight.py > control-preflight.json
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 33554432
tool=/home/hclau/ecdsa_research/product-order-20261019/target/release/trace_control
sha256sum "$tool" guard-colored.ops.bin run-control.sh > CONTROL-SOURCE.sha256
/usr/bin/time -v "$tool" ../product-pareto-20261019/parent/ops.bin ../product-pareto-20261019/parent/ops.bin guard-colored.ops.bin TRANSCRIPT-CONTROL.json > control.log 2>&1
