#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product-parent-sat-20261019
trap 'rc=$?; printf "%s\n" "$rc" > seeded.exit' EXIT
date -Is > seeded-started.txt
uptime > seeded-resources.txt
free -g >> seeded-resources.txt
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 67108864
source /home/hclau/.cargo/env
sha256sum Cargo.toml export.rs io.rs prove.py run_seeded.py run-seeded.sh > SEEDED-SOURCE.sha256
cargo test --release --offline > export-tests.log 2>&1
cargo build --release --offline > export-build.log 2>&1
python3 prove.py test > seeded-tests.log 2>&1
target/release/export /home/hclau/ecdsa_research/product-exact-20261015/product-to67-rank-20261016/product-67-retained-1024-proxy.bin /home/hclau/ecdsa_research/product-pareto-20261019/parent4-transfer/leases.json . > export.log 2>&1
sha256sum boundary-*.json GLOBAL-PROPERTIES.json > BOUNDARY-SHA256.txt
ulimit -v 16777216
python3 run_seeded.py > seeded-screen.log 2>&1
