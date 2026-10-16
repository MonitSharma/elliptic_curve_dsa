#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/current-value-attribution-20261016
echo $$ > seed-attribution.pid
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 CARGO_TARGET_DIR=/home/hclau/ecdsa_research/current-value-attribution-20261016/target-tool
{ hostname;date -Is;free -h;ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -18; } >seed-attribution-preflight.log
sha256sum ../product-exact-20261015/tip/ops.bin >seed-attribution-stream-before.sha256
python3 prepare-seed-runtime.py >seed-attribution-prepare.log 2>&1
code=$?;echo "$code" >seed-attribution-prepare.exit
if [ "$code" -ne 0 ];then exit "$code";fi
cargo build --release --offline --manifest-path tool/Cargo.toml --bin current_seed_payload >seed-attribution-build.log 2>&1
code=$?;echo "$code" >seed-attribution-build.exit
if [ "$code" -ne 0 ];then exit "$code";fi
/usr/bin/time -v target-tool/release/current_seed_payload >seed-attribution.log 2>&1
code=$?;echo "$code" >seed-attribution.exit
sha256sum ../product-exact-20261015/tip/ops.bin >seed-attribution-stream-after.sha256
exit "$code"
