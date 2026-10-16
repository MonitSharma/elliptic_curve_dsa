#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=wide-to67-scratch-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$root/$out/launcher.exit"' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 25165824
printf '%s\n' 'Predetermined Toffoli-only continuation: exactly four six-stage cycles after frozen wide43, ending67; each cycle retained128,512,1024,128,512,1024 with16 offered fresh quantum slots each stage; pair256/product1M/density/contiguous split. Extra width expressly accepted for Toffoli objective. Final67 stage count fixed before measurement; checkpoint49/55/61/67 all512 anchored full quantum/classical/phase/scratch comparisons, original MR event ordinals unchanged and separate cache-MR XOF. No packet-selected circuit/nonce/sample stop, no score claim. One analysis thread24GiB address limit; waits universal certificate terminal.' > "$out/DECLARATION.txt"
while [ ! -f cache-certificate-v2-20261016/launcher.exit ];do sleep 30;done
test "$(cat wide-to43-20261016/launcher.exit)" = 0
cp wide-to43-20261016/stage-43.manifest "$out/chain.manifest"
previous=wide-to43-20261016/wide-43-retained-1024.bin
stage=43
for cycle in 1 2 3 4;do
  for cap in 128 512 1024 128 512 1024;do
    stage=$((stage+1));name="$out/wide-$stage-retained-$cap"
    python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-preflight.json"
    EXACT_MODE=cache-retained CACHE_SPLIT=1 CACHE_RANK=density CACHE_ATOM_CAP="$cap" ANF_PAIR_CAP=256 CACHE_PRODUCT_CAP=1000000 CACHE_EXTRA_QUBITS=16 /usr/bin/time -v ./target-scratch/release/product_paired_diagnostic "$previous" "$name.bin" > "$name-generate.log" 2>&1
    if cmp -s "$previous" "$name.bin";then mapping==;else mapping="$name-generate.log";fi
    printf '%s %s\n' "$name.bin" "$mapping" >> "$out/chain.manifest"
    sha256sum "$name.bin" >> "$out/streams.sha256"
    previous="$name.bin"
  done
  cp "$out/chain.manifest" "$out/stage-$stage.manifest"
  for packet in independent structured;do
    /usr/bin/time -v ./target-anchored-replay/release/product_paired_diagnostic /home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin "$previous" "+$out/stage-$stage.manifest" "$packet" "$out/stage-$stage-$packet.tsv" > "$out/stage-$stage-$packet.log" 2>&1
  done
  python3 stream_resources.py "$previous" > "$out/stage-$stage-resources.jsonl"
done
