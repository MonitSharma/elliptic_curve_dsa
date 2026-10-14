#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/hclau/ecdsa_research/overnight-20261014/toffoli-cleanup-v27r1
cd "$ROOT"
printf '%s\n' "$$" > run.pid
trap 'rc=$?; printf "%s\n" "$rc" > run.exit; date -u --iso-8601=seconds > finished.txt; exit "$rc"' EXIT
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
date -u --iso-8601=seconds
hostname
{
    printf '%s\n' 'vmem_kib=2097152 threads=1 wall_seconds=120 rows=16384 exact_phase_closure'
    printf '%s\n' 'timeout 120 /home/hclau/ecdsa_research/.venv/bin/python toffoli_consumer_cleanup_v27r1.py constructor-netlist.json --output raw-receipt.json'
    sha256sum *.py constructor-netlist.json
} > settings.txt
/usr/bin/time -v timeout 120 /home/hclau/ecdsa_research/.venv/bin/python toffoli_consumer_cleanup_v27r1.py constructor-netlist.json --output raw-receipt.json
