#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/rng-sensitivity-arbitrary.pid
trap 'echo $? > evidence/rng-sensitivity-arbitrary.exit' EXIT
for which in tip product; do
 if test "$which" = tip; then OPS=/home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin; else OPS=/home/hclau/ecdsa_research/product-exact-20261015/chain-retained.bin; fi
 tool/target/release/rng_sensitivity "$OPS" packets/sensitivity-arbitrary.tsv "evidence/rng-sensitivity-$which-arbitrary.witnesses.jsonl" > "evidence/rng-sensitivity-$which-arbitrary.json" 2> "evidence/rng-sensitivity-$which-arbitrary.log" || exit $?
done
