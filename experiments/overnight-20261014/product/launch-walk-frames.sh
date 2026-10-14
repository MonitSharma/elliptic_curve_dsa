#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014
for kind in c5 b3; do
 if test "$kind" = c5; then base=$root/product-h45-fold-trace; ref=c5bb1ec876db859a3f9f8a9052c140a145df834e; else base=$root/product-b3-baseline; ref=b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7; fi
 checkout=$root/product-$kind-walk-frames
 evidence=$root/product-evidence/$kind-walk-frames
 test ! -e "$checkout"
 git -C "$base" worktree add --detach "$checkout" "$ref"
 mkdir -p "$evidence/run"
 python3 "$root/product-evidence/prepare-walk-frames.py" "$base" "$checkout/src/point_add" "$evidence"
 nohup bash "$root/product-evidence/server-walk-frames.sh" "$kind" > "$evidence/run.log" 2>&1 < /dev/null &
 printf '%s\n' "$!" > "$evidence/run.pid"
 echo "$kind PID $(cat "$evidence/run.pid") $evidence/run.log"
done
