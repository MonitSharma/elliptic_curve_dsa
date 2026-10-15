#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/value-carry-contracts-20261016
echo $$ > protected-square.pid
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
cp protected.json protected-y15-v1.json
cp protected-source.json protected-source-y15-v1.json
cp terminal-proof.json terminal-proof-y15-v1.json
cp prove-terminal.py prove-terminal-y15-v1.py
python3 prepare-protected.py >protected-square-prepare.log 2>&1
code=$?;echo "$code" >protected-square-prepare.exit
if [ "$code" -ne 0 ];then exit "$code";fi
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/value-carry-contracts-20261016/target-tool
cargo build --release --locked --offline --manifest-path tool/Cargo.toml --bin protected_terminal >protected-square-build.log 2>&1
code=$?;echo "$code" >protected-square-build.exit
if [ "$code" -ne 0 ];then exit "$code";fi
"$CARGO_TARGET_DIR/release/protected_terminal" >protected-square.json 2>protected-square.log
code=$?;echo "$code" >protected-square.exit
exit "$code"
