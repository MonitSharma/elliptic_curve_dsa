#!/bin/bash
set -u
ulimit -c 0
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/rng-sensitivity.pid
trap 'echo $? > /home/hclau/ecdsa_research/prefilter-20261015/evidence/rng-sensitivity.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1
free -m > evidence/rng-sensitivity.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -45 >> evidence/rng-sensitivity.resources
python3 prepare-sensitivity.py > evidence/rng-sensitivity-fixtures.json || exit $?
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin rng_sensitivity > evidence/rng-sensitivity.build.log 2>&1 || exit $?
for which in tip product; do
 if test "$which" = tip; then OPS=/home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin; else OPS=/home/hclau/ecdsa_research/product-exact-20261015/chain-retained.bin; fi
 for fixture in all-failing-tip sensitivity-structured; do
  tool/target/release/rng_sensitivity "$OPS" "packets/$fixture.tsv" "evidence/rng-sensitivity-$which-$fixture.witnesses.jsonl" > "evidence/rng-sensitivity-$which-$fixture.json" 2> "evidence/rng-sensitivity-$which-$fixture.log" || exit $?
 done
done
exit 0
