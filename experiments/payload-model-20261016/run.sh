#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/payload-model-20261016
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
hostname > preflight.log
date -Is >> preflight.log
uptime >> preflight.log
free -h >> preflight.log
ps -eo pid,comm,nlwp,pcpu,rss,args --sort=-pcpu | head -20 >> preflight.log
python3 prepare.py > prepare.log 2>&1
code=$?;echo "$code" > prepare.exit
if [ "$code" -ne 0 ];then exit "$code";fi
cd observer-tip
cargo build --release --locked --offline --bin build_circuit > ../build.log 2>&1
code=$?;echo "$code" > ../build.exit
if [ "$code" -eq 0 ];then
 /usr/bin/time -v target/release/build_circuit > ../observer.log 2>&1
 echo "$?" > ../observer.exit
 sha256sum ops.bin > ../stream.sha256
fi
