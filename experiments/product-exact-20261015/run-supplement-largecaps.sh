#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > supplement-largecaps.pid
trap 'rc=$?; echo "$rc" > "$root/supplement-largecaps.exit"' EXIT
python3 collect.py > supplement-largecaps-collection.log 2>&1
python3 verify_archive.py > supplement-largecaps-full-verification.log 2>&1
python3 make_incremental.py supplement-largecaps-terminal-20261016 > supplement-largecaps-delivery.log 2>&1
python3 verify_incremental.py evidence-through-repair53-qualification-20261016.tar.gz supplement-largecaps-terminal-20261016.tar.gz > supplement-largecaps-verification.log 2>&1
