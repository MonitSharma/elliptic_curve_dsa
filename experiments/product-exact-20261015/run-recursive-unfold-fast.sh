#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=recursive-unfold-fast-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$root/$out/launcher.exit"' EXIT
source /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/build-preflight.json"
python3 prepare_recursive_unfold_fast.py > "$out/prepare.log" 2>&1
CARGO_TARGET_DIR="$root/target-recursive-unfold-fast" cargo test --manifest-path recursive-unfold-fast-tool/Cargo.toml --release --locked --offline --bin product_paired_diagnostic interned_anf_retained -- --test-threads=1 > "$out/support-native-tests.log" 2>&1
CARGO_TARGET_DIR="$root/target-recursive-unfold-fast" cargo test --manifest-path recursive-unfold-fast-tool/Cargo.toml --release --locked --offline --bin product_paired_diagnostic lazy_cache_retained -- --test-threads=1 > "$out/cache-native-tests.log" 2>&1
CARGO_TARGET_DIR="$root/target-recursive-unfold-fast" cargo build --manifest-path recursive-unfold-fast-tool/Cargo.toml --release --locked --offline --bin product_paired_diagnostic > "$out/build.log" 2>&1
python3 replace_recursive_slow.py > "$out/replacement.log" 2>&1
bash run-recursive-unfold-fast-analysis.sh
