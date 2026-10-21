#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product-pareto-20261019
echo $$ > discovery.pid
trap 'echo $? > discovery.exit' EXIT
source /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
date -Is > started.txt
uptime > resources.txt
free -h >> resources.txt
ps -eo pid,ppid,pcpu,pmem,etime,args --sort=-pcpu | head -20 >> resources.txt
cargo test --release --manifest-path Cargo.toml > tests.log 2>&1
cargo build --release --manifest-path Cargo.toml > build-tool.log 2>&1
# Separate target storage; preserve the public source and all historical builds.
(cd parent; CARGO_TARGET_DIR=../target-parent RUSTFLAGS='-C target-cpu=native' cargo build --release --locked --bin build_circuit > ../parent-build.log 2>&1; ../target-parent/release/build_circuit > ../parent-generate.log 2>&1)
sha256sum parent/ops.bin > parent-stream.sha256
echo '99edb1d39f94c40752cb1fa2581dd2b13fe17696c486f542b8d43c1af1974683  parent/ops.bin' | sha256sum -c
target/release/product_pareto_exact parent/ops.bin parent-exact 256 > parent-scan.log 2>&1
target/release/product_pareto_exact /home/hclau/ecdsa_research/product179-native-20261017/candidate/ops.bin product179-exact 256 > product179-scan.log 2>&1
