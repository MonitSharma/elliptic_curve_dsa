#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/value-carry-contracts-20261016
echo $$ >whole-square.pid
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
cp whole_square_window.rs tool/src/bin/whole_square_window.rs
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/value-carry-contracts-20261016/target-tool
cargo build --release --locked --offline --manifest-path tool/Cargo.toml --bin whole_square_window >whole-square-build.log 2>&1
code=$?;echo "$code" >whole-square-build.exit
if [ "$code" -ne 0 ];then exit "$code";fi
"$CARGO_TARGET_DIR/release/whole_square_window" square_carry.bin square-interfaces.json >whole-square.json 2>whole-square.log
code=$?;echo "$code" >whole-square.exit
exit "$code"
