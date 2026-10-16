#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > supplement-repaired67.pid
trap 'rc=$?; echo "$rc" > "$root/supplement-repaired67.exit"' EXIT
ulimit -v 8388608
python3 /home/hclau/ecdsa_research/server-preflight.py > supplement-repaired67-preflight.json
python3 collect.py > supplement-repaired67-collection.log 2>&1
python3 verify_archive.py > supplement-repaired67-full-verification.log 2>&1
python3 make_incremental.py supplement-repaired67-qualified-20261016 > supplement-repaired67-delivery.log 2>&1
python3 verify_incremental.py evidence-through-repair53-qualification-20261016.tar.gz supplement-repaired67-qualified-20261016.tar.gz > supplement-repaired67-verification.log 2>&1
