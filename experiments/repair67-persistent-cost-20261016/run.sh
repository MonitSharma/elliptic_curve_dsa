#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/repair67-persistent-cost-20261016
echo $$ > run.pid
trap 'rc=$?; echo "$rc" > run.exit' EXIT
hostname
free -h
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -24 || true
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
timeout --signal=TERM --kill-after=20 1800 python3 -u run.py
