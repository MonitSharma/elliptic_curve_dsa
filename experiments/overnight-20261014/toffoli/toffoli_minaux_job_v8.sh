#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/hclau/ecdsa_research/overnight-20261014/toffoli-minaux-v8
cd "$ROOT"
printf '%s\n' "$$" > run.pid
trap 'rc=$?; printf "%s\n" "$rc" > run.exit; date -u --iso-8601=seconds > finished.txt; exit "$rc"' EXIT
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
date -u --iso-8601=seconds
hostname
{
    printf '%s\n' 'vmem_kib=2097152 threads=1 seconds=600 factor_timeout=5 interfaces=89 selected_raw_monomial_cosets full_truth_rows=16384'
    printf '%s\n' '/home/hclau/ecdsa_research/.venv/bin/python toffoli_minaux_interfaces_v8.py constructor-netlist.json --seconds 600 --factor-timeout 5 --output raw-receipt.json'
    sha256sum toffoli_minaux_interfaces_v8.py toffoli_guided_joint.py toffoli_quadratic_closure.py toffoli_factor_solver.py constructor-netlist.json
    /home/hclau/ecdsa_research/.venv/bin/python -c 'import z3; print("z3="+z3.get_version_string())'
} > settings.txt
/usr/bin/time -v /home/hclau/ecdsa_research/.venv/bin/python toffoli_minaux_interfaces_v8.py constructor-netlist.json --seconds 600 --factor-timeout 5 --output raw-receipt.json
