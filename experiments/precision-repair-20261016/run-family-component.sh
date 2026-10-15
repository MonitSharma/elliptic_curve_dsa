#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/precision-repair-20261016
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=3 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
{ hostname; date -Is; uptime; free -h; ps -eo pid,comm,nlwp,pcpu,rss,args --sort=-pcpu | head -20; } > preflight-family-component.log
python3 prepare-family-component.py > prepare-family-component.log 2>&1
code=$?;echo "$code" > prepare-family-component.exit
if [ "$code" -ne 0 ];then exit "$code";fi
cd component-family16
export CARGO_TARGET_DIR=../observer-tip/target
cp ../observer-tip/target/release/build_circuit ../component-top1-build_circuit
cargo build --release --locked --offline --bin build_circuit > ../build-family-component.log 2>&1
code=$?;echo "$code" > ../build-family-component.exit
if [ "$code" -ne 0 ];then exit "$code";fi
/usr/bin/time -v ../observer-tip/target/release/build_circuit > ../family-component.log 2>&1
echo "$?" > ../family-component.exit
