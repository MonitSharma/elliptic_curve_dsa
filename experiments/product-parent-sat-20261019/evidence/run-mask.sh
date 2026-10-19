#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product-parent-sat-20261019
trap 'rc=$?; printf "%s\n" "$rc" > mask.exit' EXIT
date -Is > mask-started.txt
uptime > mask-resources.txt
free -g >> mask-resources.txt
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 67108864
source /home/hclau/.cargo/env
sha256sum Cargo.toml verify_mask.rs taint.rs io.rs VERIFIED-PROOFS.json run-mask.sh > MASK-SOURCE.sha256
cargo build --release --offline --bin verify_mask > mask-build.log 2>&1
target/release/verify_mask /home/hclau/ecdsa_research/product-exact-20261015/product-to67-rank-20261016/product-67-retained-1024-proxy.bin /home/hclau/ecdsa_research/product-pareto-20261019/parent/ops.bin /home/hclau/ecdsa_research/product-pareto-20261019/parent4-transfer/leases.json PUBLIC-PARENT-MASK-TRANSFER.json VERIFIED-PROOFS.json > mask-verify.log 2>&1
sha256sum PUBLIC-PARENT-MASK-TRANSFER.json > MASK-TRANSFER.sha256
