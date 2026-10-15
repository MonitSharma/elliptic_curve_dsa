#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/value-carry-contracts-20261016
echo $$ > dirty-square-proofs.pid
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
cp protected-square.json protected-clean-square-v2.json
cp protected-source.json protected-source-clean-square-v2.json
python3 prepare-protected.py >dirty-square-prepare.log 2>&1
code=$?;echo "$code" >dirty-square-prepare.exit
if [ "$code" -ne 0 ];then exit "$code";fi
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/value-carry-contracts-20261016/target-tool
cargo build --release --locked --offline --manifest-path tool/Cargo.toml --bin protected_terminal >dirty-square-build.log 2>&1
code=$?;echo "$code" >dirty-square-build.exit
if [ "$code" -ne 0 ];then exit "$code";fi
"$CARGO_TARGET_DIR/release/protected_terminal" >protected-dirty-square.json 2>protected-dirty-square.log
code=$?;echo "$code" >protected-dirty-square.exit
if [ "$code" -ne 0 ];then exit "$code";fi
python3 prove-terminal.py >terminal-proof-dirty.log 2>&1
code=$?;echo "$code" >terminal-proof-dirty.exit
exit "$code"
