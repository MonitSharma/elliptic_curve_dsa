#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014
checkout=$root/product-repair57-production-pool
evidence=$root/product-evidence/repair57-production-pool
test ! -e "$checkout"
git -C "$root/product-h45-fold-trace" worktree add --detach "$checkout" c5bb1ec876db859a3f9f8a9052c140a145df834e
mkdir -p "$evidence/run"
python3 "$root/product-evidence/repair57-production-pool-prepare.py" "$checkout" "$checkout/src/point_add" "$evidence"
nohup bash "$root/product-evidence/repair57-production-pool-server.sh" > "$evidence/run.log" 2>&1 < /dev/null &
echo "$!" > "$evidence/run.pid"
echo "PID $(cat "$evidence/run.pid") $evidence/run.log"
