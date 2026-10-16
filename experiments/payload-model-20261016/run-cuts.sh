#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/payload-model-20261016
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1
date -Is > preflight-cuts.log
uptime >> preflight-cuts.log
free -h >> preflight-cuts.log
ps -eo pid,comm,nlwp,pcpu,rss,args --sort=-pcpu | head -20 >> preflight-cuts.log
cd cut-tool
cargo build --release --locked --offline > ../build-cuts.log 2>&1
code=$?;echo "$code" > ../build-cuts.exit
if [ "$code" -eq 0 ];then /usr/bin/time -v target/release/product_paired_diagnostic > ../cuts.log 2>&1;echo "$?" > ../cuts.exit;fi
