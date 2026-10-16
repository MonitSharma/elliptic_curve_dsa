#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/payload-model-20261016
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
date -Is > preflight-probe.log
uptime >> preflight-probe.log
free -h >> preflight-probe.log
ps -eo pid,comm,nlwp,pcpu,rss,args --sort=-pcpu | head -20 >> preflight-probe.log
python3 prepare-t0-probe.py > prepare-probe.log 2>&1
code=$?;echo "$code" > prepare-probe.exit
if [ "$code" -ne 0 ];then exit "$code";fi
cd observer-tip
cargo build --release --locked --offline --bin build_circuit > ../build-probe.log 2>&1
code=$?;echo "$code" > ../build-probe.exit
if [ "$code" -eq 0 ];then PAYLOAD_MODEL_PROBE=1 /usr/bin/time -v target/release/build_circuit > ../probe.log 2>&1;echo "$?" > ../probe.exit;fi
