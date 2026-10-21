#!/bin/bash
set -euo pipefail
ulimit -c 0
cd /home/hclau/ecdsa_research/product-pareto-20261019
test ! -e parent4-transfer-v2.pid
echo $$ > parent4-transfer-v2.pid
trap 'echo $? > parent4-transfer-v2.exit' EXIT
source /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
python3 retry_parent4_transfer.py
cd parent4-transfer-v2
cargo build --release --locked --offline --bin verify_parent_extension > build.log 2>&1
ulimit -v $((32*1024*1024))
target/release/verify_parent_extension \
  /home/hclau/ecdsa_research/product-exact-20261015/product-to67-rank-20261016/product-67-retained-1024-proxy.bin \
  ../parent/ops.bin leases.json PUBLIC-PARENT-TRANSFER.json > verify.log 2>&1
