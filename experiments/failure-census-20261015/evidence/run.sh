#!/usr/bin/env bash
# Failure-rate census: independent labelled inputs, unchanged protected simulator.
# Diagnostic only; never selects streams, nonces or packets. score=NONE.
set -euo pipefail
cd /home/hclau/ecdsa_research/failure-census-20261015
THREADS=${THREADS:-16}
BATCHES=${BATCHES:-4096}
mkdir -p results logs
{ date -Is; hostname; nproc; uptime; free -g; } > logs/preflight.txt
sha256sum target/release/failure_census census/src/main.rs census/Cargo.toml census/Cargo.lock \
  ../overnight-20261014/product-b3-baseline/src/sim.rs \
  ../overnight-20261014/product-b3-baseline/src/circuit.rs \
  ../overnight-20261014/product-b3-baseline/src/weierstrass_elliptic_curve.rs > logs/tool.sha256
while read -r name path; do
  sha256sum "$path" > "results/$name.stream.sha256"
  /usr/bin/time -f "wall=%e rss_kb=%M exit=%x" target/release/failure_census "$path" "census-$name" 0 "$BATCHES" "$THREADS" "results/$name.jsonl" 2> "logs/$name.err"
  echo "$name exit=$?" >> logs/status.txt
done <<'LIST'
b3 ../overnight-20261014/product-evidence/b3-baseline/run/ops.bin
control ../dynamic-pool-20261015/control-b3/ops.bin
wide ../dynamic-pool-20261015/wide-b3/ops.bin
LIST
echo done > run.exit
