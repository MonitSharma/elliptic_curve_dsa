#!/bin/bash
# Frozen parent4, four ascending interleaved workers, lowest passing nonce only.
set -euo pipefail
cd /home/hclau/ecdsa_research/parent4-operational-sat-20261019
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/parent4-operational-sat-20261019/search.exit' EXIT
date -Is > search-started.txt
export OMP_NUM_THREADS=1 RAYON_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
test "$(cat prepare-v2.exit)" = 0
python3 refresh_record.py > public-before-search.log 2>&1
python3 preflight.py > search-preflight.json
export SEARCH_THREADS_EACH=$(python3 -c 'import json;print(json.load(open("search-preflight.json"))["threads_each"])')
sha256sum coordinator.py preflight.py run-search.sh search.rs ACCEPTANCE.json CONTROL.json > SEARCH-SOURCE.sha256
ulimit -v 12582912
python3 coordinator.py > search.log 2>&1
