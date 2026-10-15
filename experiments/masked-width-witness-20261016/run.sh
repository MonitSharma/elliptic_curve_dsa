#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/masked-width-witness-20261016
echo $$ > run.pid
trap 'echo $? > run.exit' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 RAYON_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 16777216
python3 prepare.py > prepare.log 2>&1
cd tool
cargo build --locked --offline --release > ../build.log 2>&1
cd ..
python3 run.py > validation.log 2>&1
