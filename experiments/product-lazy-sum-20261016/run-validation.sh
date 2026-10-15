#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/hclau/ecdsa_research/product-lazy-sum-20261016
cd "$ROOT"
echo $$ > validation.pid
trap 'rc=$?; echo "$rc" > "$ROOT/validation.exit"' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > validation-preflight.json
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 prepare.py > prepare.log 2>&1
(cd tool; cargo build --release --locked --offline > ../build.log 2>&1)
python3 validate.py > validation.log 2>&1
