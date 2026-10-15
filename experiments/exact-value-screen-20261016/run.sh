#!/bin/bash
set -euo pipefail
root=/home/hclau/ecdsa_research/exact-value-screen-20261016
cd "$root"
trap 'echo $? > /home/hclau/ecdsa_research/exact-value-screen-20261016/run.exit' EXIT
hostname > hostname.log
uptime > resources-before.log
free -g >> resources-before.log
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
. /home/hclau/.cargo/env
python3 prepare.py
gcc -O3 -march=native -fPIC -shared value8.c -o libvalue8.so
cd tool
cargo build --release > ../build.log 2>&1
cd "$root"
ops=/home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin
model=/home/hclau/ecdsa_research/prefilter-20261015/model-source
VALUE_SHADOW=1 ./tool/target/release/value_prefilter "$ops" 1 128 2 shadow128.jsonl "$model" 128 > shadow128.log 2> shadow128.err
./tool/target/release/value_prefilter "$ops" 1 1024 2 timing1024-t2.jsonl "$model" 1024 > timing1024-t2.log 2> timing1024-t2.err
./tool/target/release/value_prefilter "$ops" 1 1024 16 timing1024-t16.jsonl "$model" 1024 > timing1024-t16.log 2> timing1024-t16.err
VALUE_SHADOW=1 ./tool/target/release/value_prefilter "$ops" 1046072871510 1 1 positive.jsonl "$model" 1 > positive.log 2> positive.err
VALUE_SHADOW=1 ./tool/target/release/value_prefilter "$ops" 17 11 3 partial.jsonl "$model" 9 > partial.log 2> partial.err
sha256sum libvalue8.so tool/target/release/value_prefilter > frozen.sha256
