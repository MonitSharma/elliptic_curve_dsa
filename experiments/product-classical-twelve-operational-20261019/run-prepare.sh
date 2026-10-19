#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-classical-twelve-operational-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-classical-twelve-operational-20261019/prepare.exit' EXIT
test "$(cat ../product-classical-twelve-native-20261019/gate.exit)" = 0
test "$(cat ../product-classical-twelve-filter-20261019/qualification.exit)" = 0
python3 ../autonomous-20261019/preflight_v15.py > prepare-preflight.json
sha256sum prepare.py accept.py control.py coordinator.py run-prepare.sh ../autonomous-20261019/preflight_v15.py > PREPARATION_SOURCE.sha256
ulimit -v 33554432
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1 MKL_NUM_THREADS=1 RUSTUP_TOOLCHAIN=stable
unset CARGO_TARGET_DIR
python3 prepare.py > prepare.log 2>&1
(
 trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-classical-twelve-operational-20261019/build.exit' EXIT
 cd tool
 cargo test --release --locked --offline --bin value_prefilter search_order_tests -- --test-threads=1 > ../order-tests.log 2>&1
 cargo build --release --locked --offline --bin value_prefilter > ../build.log 2>&1
)
python3 accept.py > acceptance.log 2>&1
