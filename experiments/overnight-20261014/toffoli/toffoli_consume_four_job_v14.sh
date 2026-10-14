#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/hclau/ecdsa_research/overnight-20261014/toffoli-consume-four-v14
cd "$ROOT"
printf '%s\n' "$$" > run.pid
trap 'rc=$?; printf "%s\n" "$rc" > run.exit; date -u --iso-8601=seconds > finished.txt; exit "$rc"' EXIT
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
date -u --iso-8601=seconds
hostname
{
    printf '%s\n' 'vmem_kib=2097152 threads=1 seconds=900 factor_timeout=5 full_truth_rows=262144 external_interfaces=152 rank=44 value_AND_budget=25'
    printf '%s\n' '/home/hclau/ecdsa_research/.venv/bin/python toffoli_consume_four_aux_v14.py consume-four-netlist-v13.json --seconds 900 --factor-timeout 5 --output raw-receipt.json'
    sha256sum *.py consume-four-netlist-v13.json consume-four-aux-v14-description.json
    /home/hclau/ecdsa_research/.venv/bin/python -c 'import z3; print("z3="+z3.get_version_string())'
} > settings.txt
/usr/bin/time -v /home/hclau/ecdsa_research/.venv/bin/python toffoli_consume_four_aux_v14.py consume-four-netlist-v13.json --seconds 900 --factor-timeout 5 --output raw-receipt.json
