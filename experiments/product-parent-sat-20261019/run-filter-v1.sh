#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product-parent-sat-20261019
trap 'rc=$?; printf "%s\n" "$rc" > filter.exit' EXIT
date -Is > filter-started.txt
uptime > filter-resources.txt
free -g >> filter-resources.txt
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 67108864
source /home/hclau/.cargo/env
sha256sum prepare_filter.py run-filter.sh > FILTER-SOURCE.sha256
deadline=$((SECONDS+900))
while [ ! -f extension.exit ]; do
  test "$SECONDS" -lt "$deadline"
  sleep 5
done
test "$(cat extension.exit)" = 0
python3 prepare_filter.py > filter-prepare.log 2>&1
cd parent4-filter/tool
cargo build --release --locked --offline > ../build.log 2>&1
cd ..
sha256sum tool/target/release/value_prefilter > binary-before.sha256
python3 validate.py > validation.log 2>&1
sha256sum tool/target/release/value_prefilter > binary-after.sha256
