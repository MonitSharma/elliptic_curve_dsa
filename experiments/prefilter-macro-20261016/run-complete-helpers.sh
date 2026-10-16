#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-macro-20261016
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
{ hostname;date -Is;uptime;free -h;ps -eo pid,comm,nlwp,pcpu,rss,args --sort=-pcpu | head -15; } > additional/preflight-complete-helpers.log
python3 prepare-complete-helpers.py > additional/prepare-complete-helpers.log 2>&1
code=$?;echo "$code" > additional/prepare-complete-helpers.exit
if [ "$code" -ne 0 ];then exit "$code";fi
cd observer-tip
export CARGO_TARGET_DIR=../../precision-repair-20261016/observer-tip/target
cp "$CARGO_TARGET_DIR/release/build_circuit" ../additional/carry-map-build_circuit
cargo build --release --locked --offline --bin build_circuit > ../additional/build-complete-helpers.log 2>&1
code=$?;echo "$code" > ../additional/build-complete-helpers.exit
if [ "$code" -ne 0 ];then exit "$code";fi
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" > ../additional/observer-complete-helpers.log 2>&1
code=$?;echo "$code" > ../additional/complete-helpers.exit
sha256sum ../raw-builder.bin > ../additional/raw-complete-helpers.sha256
exit "$code"
