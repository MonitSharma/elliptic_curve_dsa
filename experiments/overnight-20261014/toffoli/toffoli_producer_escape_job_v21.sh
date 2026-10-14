#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/hclau/ecdsa_research/overnight-20261014/toffoli-producer-v21
cd "$ROOT"
printf '%s\n' "$$" > run.pid
trap 'rc=$?; printf "%s\n" "$rc" > run.exit; date -u --iso-8601=seconds > finished.txt; exit "$rc"' EXIT
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
date -u --iso-8601=seconds
hostname
{
    printf '%s\n' 'vmem_kib=2097152 threads=1 solver_seconds=120 admitted_rows=11776 layout_rows=16384 monomials=1771 equations=1238'
    printf '%s\n' '/home/hclau/ecdsa_research/.venv/bin/python toffoli_producer_escape_solve_v21.py constructor-netlist.json producer-escape-v21-equations.json --seconds 120 --query query.smt2 --output raw-receipt.json'
    sha256sum *.py constructor-netlist.json producer-range-v21-description.json producer-escape-v21-equations.json
    /home/hclau/ecdsa_research/.venv/bin/python -c 'import z3; print("z3="+z3.get_version_string())'
} > settings.txt
/usr/bin/time -v /home/hclau/ecdsa_research/.venv/bin/python toffoli_producer_escape_solve_v21.py constructor-netlist.json producer-escape-v21-equations.json --seconds 120 --query query.smt2 --output raw-receipt.json
/usr/bin/time -v /home/hclau/ecdsa_research/.venv/bin/python toffoli_producer_escape_audit_v21.py constructor-netlist.json producer-escape-v21-equations.json query.smt2 --output audit-receipt.json
