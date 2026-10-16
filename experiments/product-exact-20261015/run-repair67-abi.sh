#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > repair67-abi.pid
trap 'rc=$?; echo "$rc" > "$root/repair67-abi.exit"' EXIT
ulimit -v 8388608
python3 /home/hclau/ecdsa_research/server-preflight.py > repair67-abi-preflight.json
cpu=$(python3 -c 'import os; print(max(os.sched_getaffinity(0))-1)')
exec_pid=$$
taskset -c "$cpu" python3 write_repair67_abi.py > repair67-abi-details.log 2>&1
