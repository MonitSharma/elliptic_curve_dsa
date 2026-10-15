#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/simd-prefilter-20261015
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1
hostname > preflight.log
date -Is >> preflight.log
uptime >> preflight.log
free -h >> preflight.log
ps -eo pid,comm,nlwp,pcpu,rss,args --sort=-pcpu | head -20 >> preflight.log
cd tool
cargo build --release > ../build.log 2>&1
code=$?
echo "$code" > ../build.exit
if [ "$code" -eq 0 ]; then
 /usr/bin/time -v target/release/product_paired_diagnostic /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin /home/hclau/ecdsa_research/arithmetic-repair-20261015/packets/independent.tsv 5 > ../verify.log 2>&1
 echo "$?" > ../verify.exit
fi
