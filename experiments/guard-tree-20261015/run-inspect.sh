#!/bin/bash
set -euo pipefail
root=/home/hclau/ecdsa_research/guard-tree-20261015
cd "$root"
echo $$ > inspect.pid
trap 's=$?;echo "$s" > "$root/inspect.exit"' EXIT
ulimit -v 52428800
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cp tool/src/cond_pass-next-tests.rs tool/src/cond_pass.rs
cd tool
cargo test --release --offline guard_tree_ > ../tests-dirty-corrected.log 2>&1
cargo build --release --offline > ../inspect-build.log 2>&1
cd "$root"
./tool/target/release/product_paired_diagnostic inspect before-square-finish.bin 5499240 5499500 > public-region.log
