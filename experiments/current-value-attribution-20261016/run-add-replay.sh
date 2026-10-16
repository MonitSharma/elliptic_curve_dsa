#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/current-value-attribution-20261016
echo $$ > add-replay.pid
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 CARGO_TARGET_DIR=/home/hclau/ecdsa_research/current-value-attribution-20261016/target-tool
python3 prepare-add-runtime.py >add-runtime-prepare.log 2>&1
code=$?;echo "$code" >add-runtime-prepare.exit
if [ "$code" -ne 0 ];then exit "$code";fi
python3 map-add-markers.py >add-map.log 2>&1
code=$?;echo "$code" >add-map.exit
if [ "$code" -ne 0 ];then exit "$code";fi
cargo build --release --offline --manifest-path tool/Cargo.toml --bin current_adds >add-replay-build.log 2>&1
code=$?;echo "$code" >add-replay-build.exit
if [ "$code" -ne 0 ];then exit "$code";fi
/usr/bin/time -v "$CARGO_TARGET_DIR/release/current_adds" >add-replay.log 2>&1
code=$?;echo "$code" >add-replay.exit
exit "$code"
