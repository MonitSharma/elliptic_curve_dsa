#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014
checkout=$root/product-repair57-production-literal
evidence=$root/product-evidence/repair57-production-literal
test ! -e "$checkout"
git -C "$root/product-h45-fold-trace" worktree add --detach "$checkout" c5bb1ec876db859a3f9f8a9052c140a145df834e
mkdir -p "$evidence"
python3 "$root/product-evidence/repair57-production-literal-prepare.py" "$checkout" "$checkout/src/point_add" "$root/product-evidence/h45-original-fold-contexts.json" "$root/product-evidence/c5-fold75/fold-frames.tsv" "$root/phase_decision_diagram.rs" "$root/product-evidence/repair57-production-pool" "$root/product-evidence/fold75-replay-main.rs" "$root/product-evidence/walk-replay/run.log" "$root/product-evidence/repair57-prefix-snapshot"
nohup bash "$root/product-evidence/repair57-production-literal-server.sh" > "$evidence/run.log" 2>&1 < /dev/null &
echo "$!" > "$evidence/run.pid"
echo "PID $(cat "$evidence/run.pid") $evidence/run.log"
