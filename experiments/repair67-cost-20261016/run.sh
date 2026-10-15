#!/usr/bin/env bash
set -uo pipefail
cd /home/hclau/ecdsa_research/repair67-cost-20261016
hostname > preflight-hostname.txt
date -Is > preflight-time.txt
free -b > preflight-memory.txt
ps -eo pid,nlwp,pcpu,pmem,args --sort=-pcpu > preflight-processes.txt
command -v squeue > preflight-scheduler.txt 2>&1 || true
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 RAYON_NUM_THREADS=1
python3 run.py > run.log 2>&1
code=$?
printf '%s\n' "$code" > run.exit
exit "$code"
