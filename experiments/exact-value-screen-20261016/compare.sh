#!/bin/bash
set -euo pipefail
root=/home/hclau/ecdsa_research/exact-value-screen-20261016
cd "$root"
trap 'echo $? > /home/hclau/ecdsa_research/exact-value-screen-20261016/compare.exit' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > comparison-preflight.json
sha256sum /home/hclau/ecdsa_research/prefilter-20261015/tool/target/release/bucket_fast_screen tool/target/release/value_prefilter libvalue8.so > comparison-frozen.sha256
grep -q '^89ef45b85dfa5675f56f8e8fab11d426cfb44f9ca5062da59fa32742d53faddd ' comparison-frozen.sha256
ops=/home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin
model=/home/hclau/ecdsa_research/prefilter-20261015/model-source
for trial in 1 2 3; do
 for mode in original value; do
  if test "$mode" = original; then binary=/home/hclau/ecdsa_research/prefilter-20261015/tool/target/release/bucket_fast_screen; else binary=./tool/target/release/value_prefilter; fi
  "$binary" "$ops" 1 1024 16 "compare-$trial-$mode.jsonl" "$model" 1024 > "compare-$trial-$mode.log" 2> "compare-$trial-$mode.err"
 done
done
sha256sum --check comparison-frozen.sha256 > comparison-hashes-after.log
python3 analyze.py > analysis.log
