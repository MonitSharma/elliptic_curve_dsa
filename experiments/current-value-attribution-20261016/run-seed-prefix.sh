#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/current-value-attribution-20261016
echo $$ >seed-prefix.pid
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 CARGO_TARGET_DIR=/home/hclau/ecdsa_research/current-value-attribution-20261016/target-tool
{ hostname;date -Is;free -h;ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -16; } >seed-prefix-preflight.log
python3 prepare-seed-prefix.py >seed-prefix-prepare.log 2>&1
code=$?;echo "$code" >seed-prefix-prepare.exit
if [ "$code" -ne 0 ];then exit "$code";fi
cargo build --release --offline --manifest-path tool/Cargo.toml --bin seed_prefix_zeros >seed-prefix-build.log 2>&1
code=$?;echo "$code" >seed-prefix-build.exit
if [ "$code" -ne 0 ];then exit "$code";fi
/usr/bin/time -v target-tool/release/seed_prefix_zeros >seed-prefix-zeros.log 2>&1
code=$?;echo "$code" >seed-prefix-zeros.exit;exit "$code"
