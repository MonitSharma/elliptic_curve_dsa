#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/precision-family-20261016
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
{ hostname;date -Is;uptime;free -h;ps -eo pid,comm,nlwp,pcpu,rss,args --sort=-pcpu | head -20; } > preflight-component.log
python3 prepare-component.py > prepare-component.log 2>&1
code=$?;echo "$code" > prepare-component.exit
if [ "$code" -ne 0 ];then exit "$code";fi
cd component-late-forward
export CARGO_TARGET_DIR=../../precision-repair-20261016/observer-tip/target
cp "$CARGO_TARGET_DIR/release/build_circuit" ../prior-map-build_circuit
cargo build --release --locked --offline --bin build_circuit > ../build-component.log 2>&1
code=$?;echo "$code" > ../build-component.exit
if [ "$code" -ne 0 ];then exit "$code";fi
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" > ../component.log 2>&1
code=$?;echo "$code" > ../component.exit
if [ "$code" -eq 0 ];then sha256sum ../component/raw-builder.bin > ../component/raw-builder.sha256;fi
exit "$code"
