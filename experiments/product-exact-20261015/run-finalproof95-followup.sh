#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > finalproof95-followup.pid
trap 'rc=$?; echo "$rc" > "$root/finalproof95-followup.exit"' EXIT
ulimit -v 8388608
test -f repair67-universal-20261016/CACHE_EQUIVALENCE_CERTIFICATE.json
test -f PRODUCT95_FREEZE.json
test "$(cat endpoint-source-census-20261016/launcher.exit)" = 0
test "$(cat endpoint-classification.exit)" = 0
test "$(cat endpoint-proposals.exit)" = 0
python3 /home/hclau/ecdsa_research/server-preflight.py > finalproof95-followup-preflight.json
python3 collect.py > finalproof95-followup-collection.log 2>&1
python3 verify_archive.py > finalproof95-followup-full-verification.log 2>&1
python3 make_followup_incremental.py supplement-finalproof95-endpoint-20261016 > finalproof95-followup-delivery.log 2>&1
python3 verify_followup_incremental.py evidence-through-repair53-qualification-20261016.tar.gz supplement-repaired67-qualified-20261016.tar.gz supplement-finalproof95-endpoint-20261016.tar.gz > finalproof95-followup-verification.log 2>&1
