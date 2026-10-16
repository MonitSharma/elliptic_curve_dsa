#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/payload-model-20261016
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1
date -Is > preflight-model-boundaries.log
uptime >> preflight-model-boundaries.log
free -h >> preflight-model-boundaries.log
ps -eo pid,comm,nlwp,pcpu,rss,args --sort=-pcpu | head -20 >> preflight-model-boundaries.log
cd cut-tool
cargo build --release --locked --offline > ../build-model-boundaries.log 2>&1
code=$?;echo "$code" > ../build-model-boundaries.exit
if [ "$code" -eq 0 ];then
 /usr/bin/time -v target/release/product_paired_diagnostic @t0table ../source-t0-model/t0-boundaries.tsv > ../model-boundaries.log 2>&1
 echo "$?" > ../model-boundaries.exit
 target/release/product_paired_diagnostic @t0 > ../model-eight-seed-witness.log 2>&1
 echo "$?" > ../model-eight-seed-witness.exit
fi
