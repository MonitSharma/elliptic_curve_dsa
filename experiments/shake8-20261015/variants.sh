#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/shake8-20261015
echo $$ > variants.pid
trap 'rc=$?; echo "$rc" > variants.exit' EXIT
for variant in baseline full four; do
  flags=()
  if test "$variant" = full; then flags=(-DKeccakP1600times8_AVX512_fullUnrolling); fi
  if test "$variant" = four; then flags=(-DKeccakP1600times8_AVX512_implementation_config=\"4\" -DKeccakP1600times8_AVX512_unrolling=4); fi
  cc -O3 -march=skylake-avx512 -fPIC -shared "${flags[@]}" -Iinclude -IXKCP/lib/common -IXKCP/lib/low/common -IXKCP/lib/low/KeccakP-1600-times8/AVX512 shake8.c XKCP/lib/low/KeccakP-1600-times8/AVX512/KeccakP-1600-times8-AVX512.c -o "libshake8-$variant.so" > "$variant-compile.log" 2>&1
  SHAKE8_LIB="libshake8-$variant.so" python3 validate.py > "$variant-validation.log"
done
# Interleave order across candidates to limit load/temperature confounding.
for round in 1 2; do
  for variant in baseline full four; do
    SHAKE8_LIB="libshake8-$variant.so" python3 bench-select.py > "$variant-select-$round.jsonl"
  done
done
sha256sum libshake8-baseline.so libshake8-full.so libshake8-four.so > variants.sha256
