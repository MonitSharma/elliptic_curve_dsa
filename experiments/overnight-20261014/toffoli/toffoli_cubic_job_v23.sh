#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/hclau/ecdsa_research/overnight-20261014/toffoli-cubic-v23
cd "$ROOT"
printf '%s\n' "$$" > run.pid
trap 'rc=$?; printf "%s\n" "$rc" > run.exit; date -u --iso-8601=seconds > finished.txt; exit "$rc"' EXIT
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
date -u --iso-8601=seconds
hostname
{
    printf '%s\n' 'vmem_kib=2097152 threads=1 seconds=120 rows=16384 target_rank=43 AND_budget=28'
    printf '%s\n' '/home/hclau/ecdsa_research/.venv/bin/python toffoli_cubic_complete_v23.py constructor-netlist.json cubic-extension-v20-description.json --seconds 120 --output raw-receipt.json'
    sha256sum *.py constructor-netlist.json cubic-extension-v20-description.json
} > settings.txt
/usr/bin/time -v /home/hclau/ecdsa_research/.venv/bin/python toffoli_cubic_complete_v23.py constructor-netlist.json cubic-extension-v20-description.json --seconds 120 --output raw-receipt.json
