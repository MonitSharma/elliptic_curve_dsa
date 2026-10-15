#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/precision-family-20261016
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
{ hostname;date -Is;uptime;free -h;ps -eo pid,comm,nlwp,pcpu,rss,args --sort=-pcpu | head -20; } > preflight-candidate.log
python3 prepare-candidate.py > prepare-candidate.log 2>&1
code=$?;echo "$code" > prepare-candidate.exit
if [ "$code" -ne 0 ];then exit "$code";fi
rustc --edition=2021 --test -O guard-tests.rs -o guard-tests > build-guard-tests.log 2>&1
code=$?;echo "$code" > build-guard-tests.exit
if [ "$code" -ne 0 ];then exit "$code";fi
./guard-tests --test-threads=1 > guard-tests.log 2>&1
code=$?;echo "$code" > guard-tests.exit
if [ "$code" -ne 0 ];then exit "$code";fi
cd candidate
export CARGO_TARGET_DIR=../../precision-repair-20261016/candidate-one-bit-top1/target
cp "$CARGO_TARGET_DIR/release/build_circuit" ../prior-single-region-build_circuit
cargo build --release --locked --offline --bin build_circuit > ../build-candidate.log 2>&1
code=$?;echo "$code" > ../build-candidate.exit
if [ "$code" -ne 0 ];then exit "$code";fi
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" > ../candidate.log 2>&1
code=$?;echo "$code" > ../candidate.exit
if [ "$code" -eq 0 ];then sha256sum ops.bin > ../candidate-stream.sha256;fi
exit "$code"
