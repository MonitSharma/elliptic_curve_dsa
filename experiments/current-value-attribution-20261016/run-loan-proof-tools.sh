#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/current-value-attribution-20261016
echo $$ > loan-proof-tools.pid
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 CARGO_TARGET_DIR=/home/hclau/ecdsa_research/current-value-attribution-20261016/target-tool
cp protected_dirty_low.rs tool/src/bin/protected_dirty_low.rs
cargo build --release --offline --manifest-path tool/Cargo.toml --bin protected_dirty_low >dirty-low-protected-build.log 2>&1
code=$?;echo "$code" >dirty-low-protected-build.exit
if [ "$code" -ne 0 ];then exit "$code";fi
target-tool/release/protected_dirty_low >dirty-low-protected.json 2>dirty-low-protected.log
code=$?;echo "$code" >dirty-low-protected.exit
exit "$code"
