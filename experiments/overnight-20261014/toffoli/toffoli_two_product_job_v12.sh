#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/hclau/ecdsa_research/overnight-20261014/toffoli-two-product-v12
cd "$ROOT"
printf '%s\n' "$$" > run.pid
trap 'rc=$?; printf "%s\n" "$rc" > run.exit; date -u --iso-8601=seconds > finished.txt; exit "$rc"' EXIT
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
date -u --iso-8601=seconds
hostname
{
    printf '%s\n' 'vmem_kib=2097152 threads=1 solver_timeout=600 full_truth_rows=16384 parallel_products=2'
    printf '%s\n' '/home/hclau/ecdsa_research/.venv/bin/python toffoli_two_product_extension_v12.py constructor-netlist.json symplectic-interface-v10-description.json --seconds 600 --query query.smt2 --output raw-receipt.json'
    sha256sum *.py constructor-netlist.json symplectic-interface-v10-description.json
    /home/hclau/ecdsa_research/.venv/bin/python -c 'import z3; print("z3="+z3.get_version_string())'
} > settings.txt
/usr/bin/time -v /home/hclau/ecdsa_research/.venv/bin/python toffoli_two_product_extension_v12.py constructor-netlist.json symplectic-interface-v10-description.json --seconds 600 --query query.smt2 --output raw-receipt.json
