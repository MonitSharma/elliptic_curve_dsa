#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/all70-mask-feasibility-20261016
echo $$ > run.pid
trap 'rc=$?; echo "$rc" > run.exit' EXIT
ulimit -c 0
ulimit -v 25165824
hostname
free -h
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -20 || true
timeout --signal=TERM --kill-after=10 900 python3 -u run.py
