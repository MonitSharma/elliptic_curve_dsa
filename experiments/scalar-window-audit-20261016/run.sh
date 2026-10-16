#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/scalar-window-audit-20261016
echo $$ > run.pid
trap 'rc=$?; echo "$rc" > run.exit' EXIT
ulimit -v 16777216
export OMP_NUM_THREADS=1 RAYON_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
hostname
free -h
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -18 || true
python3 -u run.py
