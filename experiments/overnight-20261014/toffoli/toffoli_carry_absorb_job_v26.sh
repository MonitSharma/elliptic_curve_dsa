#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/hclau/ecdsa_research/overnight-20261014/toffoli-absorb-v26
cd "$ROOT"
printf '%s\n' "$$" > run.pid
trap 'rc=$?; printf "%s\n" "$rc" > run.exit; date -u --iso-8601=seconds > finished.txt; exit "$rc"' EXIT
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
date -u --iso-8601=seconds
hostname
{
    printf '%s\n' 'vmem_kib=2097152 threads=1 wall_seconds=120 rows=2097152 truth_rank_only'
    printf '%s\n' 'timeout 120 /home/hclau/ecdsa_research/.venv/bin/python toffoli_carry_absorb_v26.py constructor-netlist.json consume-seven-v24-netlist.json --netlist absorb-v26-netlist.json --output raw-receipt.json'
    sha256sum *.py constructor-netlist.json consume-seven-v24-netlist.json
} > settings.txt
/usr/bin/time -v timeout 120 /home/hclau/ecdsa_research/.venv/bin/python toffoli_carry_absorb_v26.py constructor-netlist.json consume-seven-v24-netlist.json --netlist absorb-v26-netlist.json --output raw-receipt.json
