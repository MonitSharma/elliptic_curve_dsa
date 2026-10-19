#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product-peak-synthesis-20261019
trap 'rc=$?; printf "%s\n" "$rc" > run.exit' EXIT
date -Is > started.txt
uptime > resources.txt
free -g >> resources.txt
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 67108864
source /home/hclau/.cargo/env
python3 fetch.py > public-refresh.log 2>&1
sha256sum Cargo.toml *.rs run.sh > SOURCE.sha256
cargo test --release --offline > tests.log 2>&1
cargo build --release --offline > build.log 2>&1
p=/home/hclau/ecdsa_research/product-pareto-20261019/parent/ops.bin
sha256sum "$p" > PARENT-STREAM.sha256
target/release/peak "$p" parent-peaks.json > parent-peaks.log 2>&1
target/release/borrow "$p" 1200 parent-borrow > parent-borrow.log 2>&1
target/release/peak /home/hclau/ecdsa_research/product-schedule-20261019/last-carry-1232.ops.bin residual-peaks.json > residual-peaks.log 2>&1
