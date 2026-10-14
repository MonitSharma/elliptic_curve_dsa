#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/hclau/ecdsa_research/overnight-20261014/toffoli-consume-v25
cd "$ROOT"
printf '%s\n' "$$" > run.pid
trap 'rc=$?; printf "%s\n" "$rc" > run.exit; date -u --iso-8601=seconds > finished.txt; exit "$rc"' EXIT
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
date -u --iso-8601=seconds
hostname
{
    printf '%s\n' 'vmem_kib=2097152 threads=1 wall_seconds=120 rows=2097152 target_rank=46 AND_budget=24'
    printf '%s\n' 'timeout 120 /home/hclau/ecdsa_research/.venv/bin/python toffoli_consume_seven_complete_v25.py consume-seven-v24-netlist.json --seconds 115 --output raw-receipt.json'
    sha256sum *.py consume-seven-v24-netlist.json
} > settings.txt
/usr/bin/time -v timeout 120 /home/hclau/ecdsa_research/.venv/bin/python toffoli_consume_seven_complete_v25.py consume-seven-v24-netlist.json --seconds 115 --output raw-receipt.json
