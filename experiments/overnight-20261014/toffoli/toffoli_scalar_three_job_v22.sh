#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/hclau/ecdsa_research/overnight-20261014/toffoli-scalar-v22
cd "$ROOT"
printf '%s\n' "$$" > run.pid
trap 'rc=$?; printf "%s\n" "$rc" > run.exit; date -u --iso-8601=seconds > finished.txt; exit "$rc"' EXIT
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
date -u --iso-8601=seconds
hostname
{
    printf '%s\n' 'vmem_kib=2097152 threads=1 solver_seconds=600 scalar_rows=128 lift_rows=16384'
    printf '%s\n' '/home/hclau/ecdsa_research/.venv/bin/python toffoli_scalar_three_v22.py constructor-netlist.json toffoli-exact-joint-20261014.json --seconds 600 --query query.smt2 --output raw-receipt.json'
    sha256sum *.py constructor-netlist.json toffoli-exact-joint-20261014.json scalar-three-v22-description.json
    /home/hclau/ecdsa_research/.venv/bin/python -c 'import z3; print("z3="+z3.get_version_string())'
} > settings.txt
/usr/bin/time -v /home/hclau/ecdsa_research/.venv/bin/python toffoli_scalar_three_v22.py constructor-netlist.json toffoli-exact-joint-20261014.json --seconds 600 --query query.smt2 --output raw-receipt.json
