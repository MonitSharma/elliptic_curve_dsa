#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-classical-twelve-operational-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-classical-twelve-operational-20261019/search.exit' EXIT
export OMP_NUM_THREADS=1 RAYON_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
# Match the reviewed/control baseline; both baseline/fast dispatch were qualified.
unset FAST_ZERO_DISPATCH PACKED_ZERO_SHADOW EARLY_FULLSTATE_SHADOW CANDIDATE_SEED_SHADOW RAIL_SHADOW FORCE_FULL_FALLBACK
test "$(cat prepare.exit)" = 0
test "$(cat control.exit)" = 0
python3 refresh_record.py > public-before-search.log 2>&1
python3 preflight_search.py > search-preflight.json
export SEARCH_THREADS_EACH=14
sha256sum coordinator.py preflight_search.py run-search.sh ACCEPTANCE.json CONTROL.json ../autonomous-20261019/preflight_v15.py > SEARCH_SOURCE.sha256
ulimit -v 12582912
python3 coordinator.py > search.log 2>&1
