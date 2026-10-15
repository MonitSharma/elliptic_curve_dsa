#!/usr/bin/env bash
# Nonce screen of the frozen `smooth` wide stream (disclosed-failure-rate standard).
# Policy, declared before running: screen nonces 1, 2, 3, ... in ascending order
# and select the LOWEST passing nonce. The circuit is not changed; only the
# 96-op identity tail moves. A B3 negative control first checks that failing
# nonces abort where the census predicts (about 17.7 failed batches/packet).
set -uo pipefail
root=/home/hclau/ecdsa_research/nonce-screen-20261015
cd "$root"; echo $$ > run.pid
S=screen/target/release/nonce_screen
B3=../overnight-20261014/product-evidence/b3-baseline/run/ops.bin
SMOOTH=../widen-walk-20261015/smooth/src-b3/ops.bin
mkdir -p control smooth
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json 2>&1 || true
sha256sum "$S" "$B3" "$SMOOTH" > inputs.sha256
/usr/bin/time -f "wall=%e rss_kb=%M exit=%x" "$S" "$B3" 1 128 32 control/b3-1-128.jsonl > control/b3.out 2> control/b3.err
/usr/bin/time -f "wall=%e rss_kb=%M exit=%x" "$S" "$SMOOTH" 1 20000 32 smooth/screen.jsonl > smooth/screen.out 2> smooth/screen.err
date -Is > run.exit
