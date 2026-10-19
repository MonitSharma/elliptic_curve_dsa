#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product-parent-sat-20261019
trap 'rc=$?; printf "%s\n" "$rc" > relations.exit' EXIT
date -Is > relations-started.txt
uptime > relations-resources.txt
free -g >> relations-resources.txt
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 67108864
source /home/hclau/.cargo/env
sha256sum Cargo.toml graph.rs io.rs prove_graph.py run-relations.sh > RELATIONS-SOURCE.sha256
cargo test --release --offline --bin graph > relations-tests.log 2>&1
cargo build --release --offline --bin graph > relations-build.log 2>&1
test "$(cat roots.exit)" = 0
target/release/graph /home/hclau/ecdsa_research/product-exact-20261015/product-to67-rank-20261016/product-67-retained-1024-proxy.bin roots-lease-02-result.json boundary-02.json relations-02.json > relations-export.log 2>&1
sha256sum relations-02.json boundary-02.json roots-lease-02-result.json > RELATION-INPUTS.sha256
python3 prove_graph.py 2 graph > graph-lease-02.log 2>&1
