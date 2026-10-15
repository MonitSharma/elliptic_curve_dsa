#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product-early-cost-20261016
echo $$ > run.pid
trap 'echo $? > run.exit' EXIT
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 RAYON_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 12582912
python3 /home/hclau/ecdsa_research/server-preflight.py > build-preflight.json
python3 prepare.py > prepare.log 2>&1
cd tool
cargo build --release --locked --offline > ../build.log 2>&1
cd ..
while [ ! -f /home/hclau/ecdsa_research/product67-native-20261016/run.exit ]; do sleep 2; done
python3 /home/hclau/ecdsa_research/server-preflight.py > cost-preflight.json
python3 run.py > validation.log 2>&1
