#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/all70-value-transfer-20261016
echo $$ > run.pid
trap 'rc=$?; echo "$rc" > run.exit' EXIT
ulimit -v 16777216
export OMP_NUM_THREADS=1 RAYON_NUM_THREADS=1
hostname
free -h
python3 -u classify.py
