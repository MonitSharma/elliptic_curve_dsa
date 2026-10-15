#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/frozen-cache-table-20261016
echo $$ > run.pid
trap 'rc=$?; echo "$rc" > /home/hclau/ecdsa_research/frozen-cache-table-20261016/run.exit' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 33554432
python3 prepare.py > prepare.log 2>&1
cd candidate
cargo test --release --locked --offline --bin build_circuit frozen_cache25::tests -- --test-threads=1 > ../native-tests.log 2>&1
cargo build --release --locked --offline --bin build_circuit > ../build.log 2>&1
/usr/bin/time -v ./target/release/build_circuit > ../generate.log 2>&1
cmp ops.bin /home/hclau/ecdsa_research/product-exact-20261015/product-continuation-20261016/product-25-retained-1024.bin
sha256sum ops.bin > ../native-stream.sha256
date -Is > ../completed-at.txt
