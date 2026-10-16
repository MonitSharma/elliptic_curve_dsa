#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=recursive-unfold-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$root/$out/launcher.exit"' EXIT
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 25165824
printf '%s\n' 'Predetermined recursive immutable-XOR normalization:64 descending expansions,4xatom-cap live terms; atomcaps128/512, pair64/product1M/density/split. Four independent cases on frozen product53 (no extra qubits) and wide43 (16 offered fresh qubits). Native recursive cancellation, restored XOR witness/phase, old cache and new scratch guard proofs required, complete512 anchored value/phase/scratch reconstruction. No nonce/packet content selection or scored claim. One analysis thread24GiB address limit; analysis waits existing factored/wide43scratch cases terminal to preserve60GiB budget.' > "$out/DECLARATION.txt"
source /home/hclau/.cargo/env
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/build-preflight.json"
python3 prepare_recursive_unfold.py > "$out/prepare.log" 2>&1
CARGO_TARGET_DIR="$root/target-recursive-unfold" cargo test --manifest-path recursive-unfold-tool/Cargo.toml --release --locked --offline --bin product_paired_diagnostic interned_anf_retained -- --test-threads=1 > "$out/support-native-tests.log" 2>&1
CARGO_TARGET_DIR="$root/target-recursive-unfold" cargo test --manifest-path recursive-unfold-tool/Cargo.toml --release --locked --offline --bin product_paired_diagnostic lazy_cache_retained -- --test-threads=1 > "$out/cache-native-tests.log" 2>&1
CARGO_TARGET_DIR="$root/target-recursive-unfold" cargo build --manifest-path recursive-unfold-tool/Cargo.toml --release --locked --offline --bin product_paired_diagnostic > "$out/build.log" 2>&1
while [ ! -f factored-cache-20261016/launcher.exit ] || [ ! -f wide43-scratch-20261016/launcher.exit ];do sleep 30;done
for family in product53 wide43;do
  if [ "$family" = product53 ];then input=product-to53-20261016/product-53-retained-1024.bin;base=tip/ops.bin;history=product-to53-20261016/stage-53.manifest;extra=0;else input=wide-to43-20261016/wide-43-retained-1024.bin;base=/home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin;history=wide-to43-20261016/stage-43.manifest;extra=16;fi
  for cap in 128 512;do
    name="$out/$family-$cap"
    python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-preflight.json"
    EXACT_MODE=cache-retained CACHE_SPLIT=1 CACHE_RANK=density CACHE_ATOM_CAP="$cap" ANF_PAIR_CAP=64 CACHE_PRODUCT_CAP=1000000 CACHE_EXTRA_QUBITS="$extra" /usr/bin/time -v ./target-recursive-unfold/release/product_paired_diagnostic "$input" "$name.bin" > "$name-generate.log" 2>&1
    if cmp -s "$input" "$name.bin";then mapping==;else mapping="$name-generate.log";fi
    cp "$history" "$name.manifest";printf '%s %s\n' "$name.bin" "$mapping" >> "$name.manifest"
    sha256sum "$name.bin" > "$name.sha256"
    for packet in independent structured;do
      /usr/bin/time -v ./target-anchored-replay/release/product_paired_diagnostic "$base" "$name.bin" "+$name.manifest" "$packet" "$name-$packet.tsv" > "$name-$packet.log" 2>&1
    done
    python3 stream_resources.py "$name.bin" > "$name-resources.jsonl"
  done
done
