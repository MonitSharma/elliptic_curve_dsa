#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/precision-repair-20261016
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
{ hostname; date -Is; uptime; free -h; ps -eo pid,comm,nlwp,pcpu,rss,args --sort=-pcpu | head -20; } > preflight-census.log
python3 prepare-census.py > prepare-census.log 2>&1
code=$?;echo "$code" > prepare-census.exit
if [ "$code" -ne 0 ];then exit "$code";fi
cd census-tool
cargo build --release --offline > ../build-census.log 2>&1
code=$?;echo "$code" > ../build-census.exit
if [ "$code" -ne 0 ];then exit "$code";fi
/usr/bin/time -v target/release/production_fold_census 1 1 audit > ../audit.log 2>&1
code=$?;echo "$code" > ../audit.exit
if [ "$code" -ne 0 ];then exit "$code";fi
/usr/bin/time -v target/release/production_fold_census 4096 7 > ../population.log 2>&1
echo "$?" > ../population.exit
