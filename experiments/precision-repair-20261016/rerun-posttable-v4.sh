#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/precision-repair-20261016
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
{ hostname; date -Is; uptime; free -h; ps -eo pid,comm,nlwp,pcpu,rss,args --sort=-pcpu | head -20; } > preflight-posttable-v4.log
cd candidate-posttable-top1
export CARGO_TARGET_DIR=../candidate-one-bit-top1/target
cargo build --release --locked --offline --bin build_circuit > ../build-posttable-v4.log 2>&1
code=$?;echo "$code" > ../build-posttable-v4.exit
if [ "$code" -ne 0 ];then exit "$code";fi
while [ ! -f ../posttable-v3.exit ];do sleep 1;done
if [ "$(cat ../posttable-v3.exit)" -eq 0 ];then cp ops.bin ../posttable-v3-ops.bin;fi
/usr/bin/time -v ../candidate-one-bit-top1/target/release/build_circuit > ../posttable-v4.log 2>&1
code=$?;echo "$code" > ../posttable-v4.exit
if [ "$code" -eq 0 ];then sha256sum ops.bin > ../posttable-v4-stream.sha256;fi
exit "$code"
