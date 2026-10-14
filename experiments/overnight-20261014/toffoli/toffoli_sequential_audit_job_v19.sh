#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/hclau/ecdsa_research/overnight-20261014/toffoli-sequential-v19
cd "$ROOT"
printf '%s\n' "$$" > audit.pid
trap 'rc=$?; printf "%s\n" "$rc" > audit.exit; date -u --iso-8601=seconds > audit.finished.txt; exit "$rc"' EXIT
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
date -u --iso-8601=seconds
hostname
{
    printf '%s\n' 'vmem_kib=2097152 threads=1 fixed_finite_exact_ANF_audit solver_query_unchanged'
    printf '%s\n' '/home/hclau/ecdsa_research/.venv/bin/python toffoli_sequential_escape_audit_v19.py constructor-netlist.json sequential-escape-v19-description.json query.smt2 --output audit-receipt.json'
    sha256sum toffoli_sequential_escape_audit_v19.py query.smt2 sequential-escape-v19-description.json
} > audit.settings.txt
/usr/bin/time -v /home/hclau/ecdsa_research/.venv/bin/python toffoli_sequential_escape_audit_v19.py constructor-netlist.json sequential-escape-v19-description.json query.smt2 --output audit-receipt.json
