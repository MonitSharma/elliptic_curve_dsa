#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/current-value-attribution-20261016
echo $$ > dirty-add-replay.pid
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 CARGO_TARGET_DIR=/home/hclau/ecdsa_research/current-value-attribution-20261016/target-tool
python3 prepare-dirty-add-replay.py >dirty-add-prepare.log 2>&1
code=$?;echo "$code" >dirty-add-prepare.exit
if [ "$code" -ne 0 ];then exit "$code";fi
cargo build --release --offline --manifest-path tool/Cargo.toml --bin current_dirty_add >dirty-add-build.log 2>&1
code=$?;echo "$code" >dirty-add-build.exit
if [ "$code" -ne 0 ];then exit "$code";fi
/usr/bin/time -v "$CARGO_TARGET_DIR/release/current_dirty_add" >dirty-add-replay.log 2>&1
code=$?;echo "$code" >dirty-add-replay.exit
exit "$code"
