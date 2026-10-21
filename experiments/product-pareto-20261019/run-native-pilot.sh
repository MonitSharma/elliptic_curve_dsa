#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product-pareto-20261019
echo $$ > native-pilot.pid
trap 'echo $? > native-pilot.exit' EXIT
source /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 prepare_chain.py parent4 /home/hclau/ecdsa_research/product-pareto-20261019/parent parent-unwrapped parent-unwrapped-retained > native-pilot-prepare.log 2>&1
(cd candidate-parent4; CARGO_TARGET_DIR=../target-parent RUSTFLAGS='-C target-cpu=native' cargo build --release --locked --bin build_circuit > ../native-pilot-build.log 2>&1; ../target-parent/release/build_circuit > ../native-pilot-generate.log 2>&1)
python3 check_native_pilot.py > native-pilot-check.log 2>&1
