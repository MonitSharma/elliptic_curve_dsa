#!/bin/bash
set -euo pipefail
root=/home/hclau/ecdsa_research/masked-witness-20261016
cd "$root"
trap 'echo $? > /home/hclau/ecdsa_research/masked-witness-20261016/run.exit' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 RAYON_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 16777216
python3 prepare.py > prepare.log 2>&1
cd tool
cargo build --release --locked --offline > ../build.log 2>&1
cd "$root"
python3 run.py > validation.log 2>&1
