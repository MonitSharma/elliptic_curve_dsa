#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product-schedule-20261019
trap 'rc=$?; printf "%s\n" "$rc" > run.exit' EXIT
date -Is > started.txt
hostname > resources.txt
uptime >> resources.txt
free -g >> resources.txt
ps -eo pid,ppid,stat,etime,%cpu,%mem,args --sort=-%cpu | head -25 >> resources.txt
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 67108864
source /home/hclau/.cargo/env
sha256sum Cargo.toml borrow.rs io.rs width_pressure.rs run.sh > SOURCE.sha256
cargo test --release --offline > tests.log 2>&1
cargo build --release --offline > build.log 2>&1
parent=/home/hclau/ecdsa_research/product-pareto-20261019/parent/ops.bin
sha256sum "$parent" > PARENT-STREAM.sha256
for cut in 1233 1232 1230 1220 1200; do
  target/release/borrow "$parent" "$cut" "borrow-$cut" > "borrow-$cut.log" 2>&1
  target/release/width_pressure "borrow-$cut.ops.bin" "width-$cut.json" > "width-$cut.log" 2>&1
done
sha256sum borrow-*.ops.bin > OUTPUT-STREAMS.sha256
python3 summarize.py
