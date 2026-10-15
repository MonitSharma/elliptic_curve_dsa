#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/phase-localization-20261016
echo $$ >observer.pid
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
python3 prepare-observer.py >prepare.log 2>&1
status=$?; echo $status >prepare.exit; [ "$status" = 0 ] || exit "$status"
CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 cargo build --release --manifest-path tool/Cargo.toml >build.log 2>&1
status=$?; echo $status >build.exit; [ "$status" = 0 ] || exit "$status"
RAYON_NUM_THREADS=1 tool/target/release/value_prefilter ../product-exact-20261015/tip/ops.bin witnesses.tsv marks.txt >trace.jsonl 2>trace.log
status=$?; echo $status >observer.exit; exit "$status"
