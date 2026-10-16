#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=scoped-cache-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$root/$out/launcher.exit"' EXIT
source /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 41943040
printf '%s\n' 'Predetermined before measurement: BoundedBoolean BDD models classical conditions (snapshotted pushes, conditional bit updates, fresh HMR variables) to rank/filter cache proposals by sum(probability)-union(probability). Support4 functions become immutable opaque atoms; exact union support12 then original independence proxy. Opaque probabilities are propagated from operands assuming independence, rather than fixed1/2. All probabilities are ranking heuristics only. No simulator packets inform selection. Scoped exact cache leases start at first use and end in lexicalLCA after last nested scope; next-write fence on cleanup controls, untouched zero donors. Global unconditional privateflag initialization plus conditional end resets preserve dirtyABI and disjoint donor reuse. No extra qubits. Separately test cap128/512/1024 starting from immutable original4b and frozen wide15, density/split/pair64/product1M. Each result requires full original-to-final anchored reconstruction on independent and structured256shots; no scored claim or nonce search.' > "$out/DECLARATION.txt"
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/build-preflight.json"
python3 prepare_scoped_cache.py > "$out/prepare.log" 2>&1
CARGO_TARGET_DIR="$root/target-scoped-cache" cargo test --manifest-path scoped-cache-tool/Cargo.toml --release --locked --offline --bin product_paired_diagnostic guard_bdd -- --test-threads=1 > "$out/bdd-native-tests.log" 2>&1
CARGO_TARGET_DIR="$root/target-scoped-cache" cargo test --manifest-path scoped-cache-tool/Cargo.toml --release --locked --offline --bin product_paired_diagnostic lazy_cache_retained -- --test-threads=1 > "$out/cache-native-tests.log" 2>&1
CARGO_TARGET_DIR="$root/target-scoped-cache" cargo build --manifest-path scoped-cache-tool/Cargo.toml --release --locked --offline --bin product_paired_diagnostic > "$out/build.log" 2>&1
CARGO_TARGET_DIR="$root/target-scoped-replay" cargo build --manifest-path scoped-replay/Cargo.toml --release --locked --offline --bin product_paired_diagnostic > "$out/replay-build.log" 2>&1
for family in product wide; do
  if [ "$family" = product ]; then
    original=tip/ops.bin;input="$original";prefix=empty
  else
    original=/home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin
    input=wide-compound-20261016/wide-15-retained-512.bin;prefix=wide-compound-20261016/chain.manifest
  fi
  for cap in 128 512 1024; do
    name="$out/$family-$cap"
    python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-preflight.json"
    EXACT_MODE=cache-retained CACHE_SPLIT=1 CACHE_RANK=density CACHE_ATOM_CAP="$cap" ANF_PAIR_CAP=64 CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./target-scoped-cache/release/product_paired_diagnostic "$input" "$name.bin" > "$name-generate.log" 2>&1
    if [ "$prefix" = empty ]; then : > "$name.manifest"; else cp "$prefix" "$name.manifest"; fi
    if cmp -s "$input" "$name.bin"; then mapping==; else mapping="$name-generate.log"; fi
    printf '%s %s\n' "$name.bin" "$mapping" >> "$name.manifest"
    sha256sum "$name.bin" > "$name.sha256"
    for packet in independent structured; do
      /usr/bin/time -v ./target-scoped-replay/release/product_paired_diagnostic "$original" "$name.bin" "+$name.manifest" "$packet" "$name-$packet.tsv" > "$name-$packet.log" 2>&1
    done
    python3 stream_resources.py "$name.bin" > "$name-resources.jsonl"
  done
done
