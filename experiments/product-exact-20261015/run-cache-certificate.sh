#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=cache-certificate-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$root/$out/launcher.exit"' EXIT
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 12582912
source /home/hclau/.cargo/env
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/preflight.json"
python3 prepare_cache_certificate.py > "$out/prepare.log" 2>&1
CARGO_TARGET_DIR="$root/target-cache-certificate" cargo test --manifest-path cache-certificate-tool/Cargo.toml --release --locked --offline --bin product_paired_diagnostic cache_certificate::tests -- --test-threads=1 > "$out/native-tests.log" 2>&1
CARGO_TARGET_DIR="$root/target-cache-certificate" cargo build --manifest-path cache-certificate-tool/Cargo.toml --release --locked --offline --bin product_paired_diagnostic > "$out/build.log" 2>&1
python3 run_cache_certificate_chain.py > "$out/chain.log" 2>&1
