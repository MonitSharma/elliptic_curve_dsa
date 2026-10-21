#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product-pareto-20261019
echo $$ > continuation84.pid
trap 'echo $? > continuation84.exit' EXIT
source /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
date -Is > continuation84-started.txt
uptime > continuation84-resources.txt
free -g >> continuation84-resources.txt
ps -eo pid,ppid,pcpu,pmem,etime,args --sort=-pcpu | head -20 >> continuation84-resources.txt
sha256sum continue84.py finish84.py gate84.py prepare_chain.py > continuation84-scripts.sha256
python3 continue84.py > continuation84-generation.log 2>&1
python3 finish84.py > continuation84-native.log 2>&1
python3 gate84.py > continuation84-gate.log 2>&1
