#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/precision-repair-20261016
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
{ hostname; date -Is; uptime; free -h; ps -eo pid,comm,nlwp,pcpu,rss,args --sort=-pcpu | head -20; } > preflight-posttable.log
python3 prepare-posttable.py > prepare-posttable.log 2>&1
code=$?;echo "$code" > prepare-posttable.exit
if [ "$code" -ne 0 ];then exit "$code";fi
cd candidate-posttable-top1
export CARGO_TARGET_DIR=../candidate-one-bit-top1/target
cp ../candidate-one-bit-top1/target/release/build_circuit ../rejected-one-bit-build_circuit
cargo build --release --locked --offline --bin build_circuit > ../build-posttable.log 2>&1
code=$?;echo "$code" > ../build-posttable.exit
if [ "$code" -ne 0 ];then exit "$code";fi
/usr/bin/time -v ../candidate-one-bit-top1/target/release/build_circuit > ../posttable.log 2>&1
code=$?;echo "$code" > ../posttable.exit
if [ "$code" -eq 0 ];then sha256sum ops.bin > ../posttable-stream.sha256;fi
exit "$code"
