#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/payload-model-20261016
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1
date -Is > preflight-t0-witness.log
uptime >> preflight-t0-witness.log
free -h >> preflight-t0-witness.log
ps -eo pid,comm,nlwp,pcpu,rss,args --sort=-pcpu | head -20 >> preflight-t0-witness.log
cd cut-tool
cargo build --release --locked --offline > ../build-t0-witness.log 2>&1
code=$?;echo "$code" > ../build-t0-witness.exit
if [ "$code" -eq 0 ];then /usr/bin/time -v target/release/product_paired_diagnostic @t0 > ../t0-witness.log 2>&1;echo "$?" > ../t0-witness.exit;fi
