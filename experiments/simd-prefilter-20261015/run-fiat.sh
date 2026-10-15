#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/simd-prefilter-20261015
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1
date -Is > preflight-fiat.log
uptime >> preflight-fiat.log
free -h >> preflight-fiat.log
ps -eo pid,comm,nlwp,pcpu,rss,args --sort=-pcpu | head -20 >> preflight-fiat.log
cd tool
cargo build --release > ../build-fiat.log 2>&1
code=$?
echo "$code" > ../build-fiat.exit
if [ "$code" -eq 0 ]; then
 /usr/bin/time -v target/release/product_paired_diagnostic @fiat /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin > ../fiat-verify.log 2>&1
 echo "$?" > ../fiat-verify.exit
fi
