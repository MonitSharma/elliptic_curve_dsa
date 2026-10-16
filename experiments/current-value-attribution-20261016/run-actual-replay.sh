#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/current-value-attribution-20261016
echo $$ > actual-replay.pid
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
{ hostname;date -Is;uptime;free -h;ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -20; } >actual-replay-preflight.log
test "$(cat map.exit)" = 0 || exit 1
sha256sum ../product-exact-20261015/tip/ops.bin >actual-replay-stream-before.sha256
grep -q 2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e actual-replay-stream-before.sha256 || exit 1
cp -a ../value-carry-contracts-20261016/target-tool target-tool >runtime-target-copy.log 2>&1
code=$?;echo "$code" >runtime-target-copy.exit
if [ "$code" -ne 0 ];then exit "$code";fi
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/current-value-attribution-20261016/target-tool
# Only the new standalone research tool adds a direct reference to the already
# installed ruint dependency; contestant Cargo and all protected sources stay
# unchanged. Resolve its private lock offline, then preserve the resulting lock.
cargo build --release --offline --manifest-path tool/Cargo.toml --bin current_payload >actual-replay-build.log 2>&1
code=$?;echo "$code" >actual-replay-build.exit
if [ "$code" -ne 0 ];then exit "$code";fi
sha256sum "$CARGO_TARGET_DIR/release/current_payload" tool/Cargo.toml tool/Cargo.lock >actual-replay-build.sha256
/usr/bin/time -v "$CARGO_TARGET_DIR/release/current_payload" >actual-replay.log 2>&1
code=$?;echo "$code" >actual-replay.exit
sha256sum ../product-exact-20261015/tip/ops.bin >actual-replay-stream-after.sha256
exit "$code"
