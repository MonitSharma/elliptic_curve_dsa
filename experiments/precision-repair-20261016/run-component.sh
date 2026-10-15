#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/precision-repair-20261016
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
{ hostname; date -Is; uptime; free -h; ps -eo pid,comm,nlwp,pcpu,rss,args --sort=-pcpu | head -20; } > preflight-component.log
python3 prepare-component.py > prepare-component.log 2>&1
code=$?;echo "$code" > prepare-component.exit
if [ "$code" -ne 0 ];then exit "$code";fi
cp observer-tip/target/release/build_circuit baseline-observer-build_circuit
sha256sum baseline-observer-build_circuit > baseline-observer-binary.sha256
cd component-observer
export CARGO_TARGET_DIR=../observer-tip/target
cargo build --release --locked --offline --bin build_circuit > ../build-component.log 2>&1
code=$?;echo "$code" > ../build-component.exit
if [ "$code" -ne 0 ];then exit "$code";fi
/usr/bin/time -v ../observer-tip/target/release/build_circuit > ../component.log 2>&1
echo "$?" > ../component.exit
