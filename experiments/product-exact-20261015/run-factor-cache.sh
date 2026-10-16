#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=factor-cache-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$root/$out/launcher.exit"' EXIT
printf '%s\n' 'Predetermined: factor arity256/512/1024, ANFatomcap128/paircap64/productcap1M, original4b and original5a, density/split/per-donorflags/noextraQ. All six cases independently start immutable original source. Native200-input AND witness +factor idempotence proof, all prior cache native tests, full operation reconstruction and anchored independent/structured256shots required. No scored claim, source/packet/nonce selection. Analysis waits for wide43 and weighted-guard terminal to keep aggregate memory below60GiB; single thread/24GiB virtual limit.' > "$out/DECLARATION.txt"
source /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 25165824
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/build-preflight.json"
python3 prepare_factor_cache.py > "$out/prepare.log" 2>&1
FACTOR_CAP=256 CARGO_TARGET_DIR="$root/target-factor-cache" cargo test --manifest-path factor-cache-tool/Cargo.toml --release --locked --offline --bin product_paired_diagnostic interned_anf_retained::anf_tests -- --test-threads=1 > "$out/factor-native-tests.log" 2>&1
CARGO_TARGET_DIR="$root/target-factor-cache" cargo test --manifest-path factor-cache-tool/Cargo.toml --release --locked --offline --bin product_paired_diagnostic lazy_cache_retained -- --test-threads=1 > "$out/cache-native-tests.log" 2>&1
CARGO_TARGET_DIR="$root/target-factor-cache" cargo build --manifest-path factor-cache-tool/Cargo.toml --release --locked --offline --bin product_paired_diagnostic > "$out/build.log" 2>&1
while [ ! -f wide-to43-20261016/launcher.exit ] || [ ! -f guard-cache-weighted-20261016/launcher.exit ]; do sleep 30; done
for family in product wide; do
  if [ "$family" = product ]; then input=tip/ops.bin;else input=/home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin;fi
  for cap in 256 512 1024; do
    name="$out/$family-$cap"
    python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-preflight.json"
    EXACT_MODE=cache-retained FACTOR_CAP="$cap" CACHE_SPLIT=1 CACHE_RANK=density CACHE_ATOM_CAP=128 ANF_PAIR_CAP=64 CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./target-factor-cache/release/product_paired_diagnostic "$input" "$name.bin" > "$name-generate.log" 2>&1
    if cmp -s "$input" "$name.bin"; then mapping==; else mapping="$name-generate.log"; fi
    printf '%s %s\n' "$name.bin" "$mapping" > "$name.manifest"
    sha256sum "$name.bin" > "$name.sha256"
    for packet in independent structured; do
      /usr/bin/time -v ./target-anchored-replay/release/product_paired_diagnostic "$input" "$name.bin" "+$name.manifest" "$packet" "$name-$packet.tsv" > "$name-$packet.log" 2>&1
    done
    python3 stream_resources.py "$name.bin" > "$name-resources.jsonl"
  done
done
