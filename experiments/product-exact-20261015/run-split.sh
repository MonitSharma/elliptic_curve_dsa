#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > split.pid
trap 'rc=$?; echo "$rc" > split.exit' EXIT
source /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 62914560
python3 /home/hclau/ecdsa_research/server-preflight.py > split-preflight.json
CACHE_SPLIT=1 CACHE_RANK=proxy ./target/release/deps/product_paired_diagnostic-418b75f8bd020e66 --nocapture > split-tests.log 2>&1
until test -f original.exit; do sleep 5; done
test "$(cat original.exit)" = 0
for cap in 32 128 512; do
  for rank in proxy density; do
    name=split-$cap-$rank
    CACHE_SPLIT=1 CACHE_RANK=$rank CACHE_ATOM_CAP=$cap CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./target/release/product_paired_diagnostic tip/ops.bin "$name.bin" > "$name-generate.log" 2>&1
    sha256sum "$name.bin" > "$name.sha256"
    python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-preflight.json"
    /usr/bin/time -v /home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census "$name.bin" product-exact-20261015 0 4096 12 "$name-census.jsonl" > "$name-census.out" 2> "$name-census.err"
  done
done
/usr/bin/time -v /home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census tip/ops.bin product-exact-20261015 0 4096 12 original-census.jsonl > original-census.out 2> original-census.err
