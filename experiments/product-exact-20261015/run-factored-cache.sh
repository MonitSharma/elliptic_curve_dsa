#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=factored-cache-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$root/$out/launcher.exit"' EXIT
printf '%s\n' 'Predetermined alternate exact factored normal form: immutable full Boolean-function factors, no ANF distribution, exact complementary-factor absorption, factorarity512, XORatomcaps128/512, cache-retained and witness-only-retained modes independently on original4b, frozen product53 and frozen wide43. All12 combinations retained, no packet-selected configuration. No added qubits; cache three private flags per donor. Independent reconstruction plus anchored value/phase/scratch comparison on256 independent and256 structured shots. Witness mode additionally identical MR/other records certified. No nonce or scored claim. One analysis thread24GiB limit; wait existing weighted/scoped/factor jobs terminal before analysis.' > "$out/DECLARATION.txt"
source /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 25165824
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/build-preflight.json"
python3 prepare_factored_cache.py > "$out/prepare.log" 2>&1
FACTOR_CAP=512 CARGO_TARGET_DIR="$root/target-factored-cache" cargo test --manifest-path factored-cache-tool/Cargo.toml --release --locked --offline --bin product_paired_diagnostic interned_anf_retained::anf_tests -- --test-threads=1 > "$out/factored-native-tests.log" 2>&1
CARGO_TARGET_DIR="$root/target-factored-cache" cargo test --manifest-path factored-cache-tool/Cargo.toml --release --locked --offline --bin product_paired_diagnostic lazy_cache_retained -- --test-threads=1 > "$out/cache-native-tests.log" 2>&1
CARGO_TARGET_DIR="$root/target-factored-cache" cargo build --manifest-path factored-cache-tool/Cargo.toml --release --locked --offline --bin product_paired_diagnostic > "$out/build.log" 2>&1
while [ ! -f factor-witness-20261016/launcher.exit ] || [ ! -f factor-cache-20261016/launcher.exit ] || [ ! -f scoped-cache-20261016/launcher.exit ]; do sleep 30; done
for family in product product53 wide43; do
  if [ "$family" = product ]; then input=tip/ops.bin;base=tip/ops.bin;history=;fi
  if [ "$family" = product53 ]; then input=product-to53-20261016/product-53-retained-1024.bin;base=tip/ops.bin;history=product-to53-20261016/stage-53.manifest;fi
  if [ "$family" = wide43 ]; then input=wide-to43-20261016/wide-43-retained-1024.bin;base=/home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin;history=wide-to43-20261016/stage-43.manifest;fi
  for cap in 128 512; do
    for mode in cache-retained witness-only-retained; do
      name="$out/$family-$cap-$mode"
      python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-preflight.json"
      EXACT_MODE="$mode" FACTOR_CAP=512 CACHE_SPLIT=1 CACHE_RANK=density CACHE_ATOM_CAP="$cap" ANF_PAIR_CAP=64 CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./target-factored-cache/release/product_paired_diagnostic "$input" "$name.bin" > "$name-generate.log" 2>&1
      if cmp -s "$input" "$name.bin"; then mapping==;else mapping="$name-generate.log";fi
      if [ "$mode" = witness-only-retained ]; then
        python3 certify_witness_rows.py "$input" "$name.bin" "$name-generate.log" > "$name-certificate.json"
        mapping==
      fi
      if [ -n "$history" ]; then cp "$history" "$name.manifest";else : > "$name.manifest";fi
      printf '%s %s\n' "$name.bin" "$mapping" >> "$name.manifest"
      sha256sum "$name.bin" > "$name.sha256"
      for packet in independent structured; do
        /usr/bin/time -v ./target-anchored-replay/release/product_paired_diagnostic "$base" "$name.bin" "+$name.manifest" "$packet" "$name-$packet.tsv" > "$name-$packet.log" 2>&1
      done
      python3 stream_resources.py "$name.bin" > "$name-resources.jsonl"
    done
  done
done
