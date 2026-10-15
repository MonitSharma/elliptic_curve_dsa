#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/value-carry-contracts-20261016
echo $$ >square-observer.pid
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
{ hostname;date -Is;free -h;ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -18; } >square-observer-preflight.log
python3 prepare-square-observer.py >square-observer-prepare.log 2>&1
code=$?;echo "$code" >square-observer-prepare.exit
if [ "$code" -ne 0 ];then exit "$code";fi
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/value-carry-contracts-20261016/target-observer
cp "$CARGO_TARGET_DIR/release/build_circuit" preserved-original-observer-build_circuit
cargo build --release --locked --offline --manifest-path square-observer/Cargo.toml --bin build_circuit >square-observer-build.log 2>&1
code=$?;echo "$code" >square-observer-build.exit
if [ "$code" -ne 0 ];then exit "$code";fi
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" >square-observer.log 2>&1
code=$?;echo "$code" >square-observer.exit
exit "$code"
