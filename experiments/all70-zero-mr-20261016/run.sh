#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/all70-zero-mr-20261016
echo $$ > run.pid
trap 'rc=$?; echo "$rc" > run.exit' EXIT
ulimit -c 0
ulimit -v 16777216
hostname
free -h
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -20 || true
timeout --signal=TERM --kill-after=15 900 python3 -u run.py
