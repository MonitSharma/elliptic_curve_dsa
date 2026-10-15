#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-macro-20261016
mkdir -p additional
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
{ hostname;date -Is;uptime;free -h;ps -eo pid,comm,nlwp,pcpu,rss,args --sort=-pcpu | head -15; } > additional/preflight-carry-helper.log
python3 prepare-carry-helper.py > additional/prepare-carry-helper.log 2>&1
code=$?;echo "$code" > additional/prepare-carry-helper.exit
if [ "$code" -ne 0 ];then exit "$code";fi
cd observer-tip
export CARGO_TARGET_DIR=../../precision-repair-20261016/observer-tip/target
cp "$CARGO_TARGET_DIR/release/build_circuit" ../additional/compare-map-build_circuit
cargo build --release --locked --offline --bin build_circuit > ../additional/build-carry-helper.log 2>&1
code=$?;echo "$code" > ../additional/build-carry-helper.exit
if [ "$code" -ne 0 ];then exit "$code";fi
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" > ../additional/observer-carry-helper.log 2>&1
code=$?;echo "$code" > ../additional/carry-helper.exit
sha256sum ../raw-builder.bin > ../additional/raw-carry-helper.sha256
exit "$code"
