#!/usr/bin/env bash
# Replay census failures under 32 independent measurement seeds. Diagnostic; score=NONE.
set -euo pipefail
cd /home/hclau/ecdsa_research/failure-census-20261015
sha256sum target/release/failure_replay replay/src/main.rs inputs/*.tsv > logs/replay-tool.sha256
for spec in "b3 ../overnight-20261014/product-evidence/b3-baseline/run/ops.bin" "control ../dynamic-pool-20261015/control-b3/ops.bin" "wide ../dynamic-pool-20261015/wide-b3/ops.bin"; do
  set -- $spec
  /usr/bin/time -f "wall=%e rss_kb=%M exit=%x" target/release/failure_replay "$2" "inputs/$1-failures.tsv" 32 16 "results/$1-replay.jsonl" 2> "logs/$1-replay.err"
done
echo done > replay.exit
