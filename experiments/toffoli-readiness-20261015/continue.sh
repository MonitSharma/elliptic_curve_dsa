#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/toffoli-readiness-20261015
echo $$ > "$root/continue.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$root/continue.exit"' EXIT
for attempt in $(seq 1 240); do
 test -f "$root/evidence/run.exit" && break
 sleep 5
done
test -f "$root/evidence/terminal/receipt.json"
(
 set -euo pipefail
 trap 'rc=$?; printf "%s\n" "$rc" > "$root/replay/run-r2.exit"' EXIT
 base=/home/hclau/ecdsa_research/overnight-20261014/product-evidence/b3-baseline/run/ops.bin
 candidate="$root/candidate-b3-cache-v1/ops.bin"
 binary="$root/replay/target/release/product_paired_diagnostic"
 sha256sum "$binary" "$base" "$candidate" "$root/replay/crate/src/main.rs" > "$root/replay/bindings-r2.sha256"
 for mode in independent structured candidate; do
  /usr/bin/time -v "$binary" "$base" "$candidate" "$root/evidence/benchmark.log" "$mode" "$root/replay/$mode.tsv" > "$root/replay/$mode.log" 2>&1
 done
 sha256sum "$root/replay"/*.tsv > "$root/replay/packets.sha256"
) &
paired_pid=$!
echo "$paired_pid" > "$root/replay-r2.pid"
# First candidate's terminal source/binary receipt is complete before the
# dedicated local build cache is reused. No other chat uses this target.
bash "$root/wide.sh"
wait "$paired_pid"
bash "$root/wide-replay.sh"
