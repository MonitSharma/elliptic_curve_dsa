#!/bin/bash
set -euo pipefail
ulimit -c 0
root=/home/hclau/ecdsa_research/product-pareto-20261019
cd "$root"
test ! -e "$root/parent4-filter-qualification-v2.pid"
echo $$ > "$root/parent4-filter-qualification-v2.pid"
trap 'echo $? > "$root/parent4-filter-qualification-v2.exit"' EXIT
while [ ! -f "$root/parent4-transfer-local.exit" ]; do sleep 10; done
test "$(cat "$root/parent4-transfer-local.exit")" = 0
source /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
python3 prepare_parent4_filter.py
cd parent4-filter/tool
cargo build --release --locked --offline > ../build.log 2>&1
cd ..
python3 -u validate.py > validation.log 2>&1
