#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/precision-repair-20261016
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
hostname > preflight-observer.log
date -Is >> preflight-observer.log
uptime >> preflight-observer.log
free -h >> preflight-observer.log
ps -eo pid,comm,nlwp,pcpu,rss,args --sort=-pcpu | head -20 >> preflight-observer.log
python3 prepare-observer.py > prepare-observer.log 2>&1
code=$?;echo "$code" > prepare-observer.exit
if [ "$code" -ne 0 ];then exit "$code";fi
cd observer-tip
cargo build --release --locked --offline --bin build_circuit > ../build-observer.log 2>&1
code=$?;echo "$code" > ../build-observer.exit
if [ "$code" -eq 0 ];then
 /usr/bin/time -v target/release/build_circuit > ../observer.log 2>&1
 echo "$?" > ../observer.exit
 sha256sum ops.bin > ../observer-stream.sha256
fi
