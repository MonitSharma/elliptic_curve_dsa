#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-macro-20261016
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
{ hostname; date -Is; uptime; free -h; ps -eo pid,comm,nlwp,pcpu,rss,args --sort=-pcpu | head -20; } > preflight-compare-ends.log
python3 prepare-compare-ends.py > prepare-compare-ends.log 2>&1
code=$?;echo "$code" > prepare-compare-ends.exit
if [ "$code" -ne 0 ];then exit "$code";fi
cd observer-tip
export CARGO_TARGET_DIR=../../precision-repair-20261016/observer-tip/target
cp ../../precision-repair-20261016/observer-tip/target/release/build_circuit ../top1-map-build_circuit
cargo build --release --locked --offline --bin build_circuit > ../build-compare-ends.log 2>&1
code=$?;echo "$code" > ../build-compare-ends.exit
if [ "$code" -ne 0 ];then exit "$code";fi
/usr/bin/time -v ../../precision-repair-20261016/observer-tip/target/release/build_circuit > ../observer.log 2>&1
code=$?;echo "$code" > ../compare-ends.exit
if [ "$code" -eq 0 ];then sha256sum ../raw-builder.bin ../../precision-repair-20261016/raw-builder.bin > ../raw-stream-bindings.sha256;fi
exit "$code"
