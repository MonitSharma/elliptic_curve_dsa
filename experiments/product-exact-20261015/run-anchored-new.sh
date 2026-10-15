#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=anchored-new-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$out/launcher.exit"' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 41943040
while [ ! -f anchored-replay-20261016/launcher.exit ]; do sleep 30; done
test "$(cat anchored-replay-20261016/launcher.exit)" = 0
for spec in product:flags-extended-20261016/product-11-retained-1024.bin:flags-extended-20261016/chain.manifest:flags-extended-20261016 wide:wide-compound-20261016/wide-15-retained-512.bin:wide-compound-20261016/chain.manifest:wide-compound-20261016; do
  IFS=: read -r track final manifest folder <<< "$spec"
  while [ ! -f "$folder/launcher.exit" ]; do sleep 30; done
  test "$(cat "$folder/launcher.exit")" = 0
  if [ "$track" = product ]; then original=tip/ops.bin; else original=/home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin; fi
  python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/$track-preflight.json"
  for family in independent structured; do
    /usr/bin/time -v ./target-anchored-replay/release/product_paired_diagnostic "$original" "$final" "+$manifest" "$family" "$out/$track-$family.tsv" > "$out/$track-$family.log" 2>&1
  done
done
