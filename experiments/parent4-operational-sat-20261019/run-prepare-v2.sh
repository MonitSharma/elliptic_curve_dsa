#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/parent4-operational-sat-20261019
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/parent4-operational-sat-20261019/prepare-v2.exit' EXIT
date -Is > prepare-v2-started.txt
uptime > prepare-v2-resources.txt
free -g >> prepare-v2-resources.txt
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 33554432
source /home/hclau/.cargo/env
deadline=$((SECONDS+1800))
while [ ! -f /home/hclau/ecdsa_research/product-parent-sat-20261019/parent4-filter/filter.exit ]; do
  test "$SECONDS" -lt "$deadline"
  sleep 5
done
test "$(cat /home/hclau/ecdsa_research/product-parent-sat-20261019/parent4-filter/filter.exit)" = 0
sha256sum prepare_port.py accept.py control.py coordinator.py search.rs run-prepare-v2.sh > PREPARE-V2-SOURCE.sha256
python3 prepare_port.py > prepare-port.log 2>&1
(
  trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/parent4-operational-sat-20261019/build.exit' EXIT
  cd tool
  cargo test --release --locked --offline --bin value_prefilter search_order_tests -- --test-threads=1 > ../order-tests.log 2>&1
  cargo build --release --locked --offline > ../build.log 2>&1
)
python3 accept.py > acceptance.log 2>&1
python3 control.py > control.log 2>&1
