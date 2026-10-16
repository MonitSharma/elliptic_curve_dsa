#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/current-value-attribution-20261016
echo $$ >all-add-replay.pid
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 CARGO_TARGET_DIR=/home/hclau/ecdsa_research/current-value-attribution-20261016/target-tool
{ hostname;date -Is;free -h;ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -18; } >all-add-replay-preflight.log
python3 prepare-all-add-replay.py >all-add-prepare.log 2>&1
code=$?;echo "$code" >all-add-prepare.exit;if [ "$code" -ne 0 ];then exit "$code";fi
sha256sum ../product-exact-20261015/tip/ops.bin actual-add-markers.json tool/src/all_add_runtime.rs tool/src/bin/current_all_adds.rs >all-add-stream-source-before.sha256
cargo build --release --offline --manifest-path tool/Cargo.toml --bin current_all_adds >all-add-build.log 2>&1
code=$?;echo "$code" >all-add-build.exit;if [ "$code" -ne 0 ];then exit "$code";fi
/usr/bin/time -v "$CARGO_TARGET_DIR/release/current_all_adds" >all-add-replay.log 2>&1
code=$?;echo "$code" >all-add-replay.exit
sha256sum ../product-exact-20261015/tip/ops.bin actual-add-markers.json tool/src/all_add_runtime.rs tool/src/bin/current_all_adds.rs >all-add-stream-source-after.sha256
cmp all-add-stream-source-before.sha256 all-add-stream-source-after.sha256 || exit 91
exit "$code"
