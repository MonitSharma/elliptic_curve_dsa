#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/all70-zero-mr-20261016
echo $$ > run-v2.pid
trap 'rc=$?; echo "$rc" > run-v2.exit' EXIT
ulimit -c 0
ulimit -v 16777216
remaining=$(python3 -c 'import pathlib,time; print(max(0,int(pathlib.Path("failed-v1/run.pid").stat().st_mtime+900-time.time())))')
test "$remaining" -gt 0
echo "Remaining original900-second wall budget: $remaining seconds"
timeout --signal=TERM --kill-after=15 "$remaining" python3 -u run.py
