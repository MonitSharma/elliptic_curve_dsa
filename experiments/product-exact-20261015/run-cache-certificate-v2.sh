#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=cache-certificate-v2-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$root/$out/launcher.exit"' EXIT
source /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/build-preflight.json"
python3 prepare_cache_certificate_v2.py > "$out/prepare.log" 2>&1
CARGO_TARGET_DIR="$root/target-cache-certificate-v2" cargo test --manifest-path cache-certificate-v2-tool/Cargo.toml --release --locked --offline --bin product_paired_diagnostic cache_certificate::tests -- --test-threads=1 > "$out/native-tests.log" 2>&1
CARGO_TARGET_DIR="$root/target-cache-certificate-v2" cargo build --manifest-path cache-certificate-v2-tool/Cargo.toml --release --locked --offline --bin product_paired_diagnostic > "$out/build.log" 2>&1
while [ ! -f cache-certificate-parallel-20261016/launcher.exit ] || [ ! -f wide43-scratch-20261016/launcher.exit ];do sleep 30;done
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/audit-preflight.json"
python3 run_cache_certificate_v2.py > "$out/chain.log" 2>&1
